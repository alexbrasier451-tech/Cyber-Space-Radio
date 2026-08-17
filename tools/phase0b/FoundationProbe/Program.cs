using System.Net;
using System.Net.Sockets;
using System.Net.WebSockets;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

const string SyntheticPassphrase = "phase-0b synthetic passphrase only";
const string PlaintextSentinel = "PHASE0B-PLAINTEXT-MUST-NOT-PERSIST";

var jsonOptions = new JsonSerializerOptions
{
    WriteIndented = true,
    PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
};
var checks = new Dictionary<string, bool>();
var notes = new List<string>();

var keyEnvelope = KeyEnvelope.Create(SyntheticPassphrase);
checks["wrong_passphrase_fails_closed"] = !keyEnvelope.TryUnwrap(
    "wrong synthetic passphrase",
    out _);

if (!keyEnvelope.TryUnwrap(SyntheticPassphrase, out var dataKey))
{
    throw new InvalidOperationException("Synthetic manual unlock failed.");
}

try
{
    var recordEnvelope = RecordEnvelope.Encrypt(PlaintextSentinel, dataKey);
    var storePath = Path.Combine(AppContext.BaseDirectory, "probe-store.json");
    await File.WriteAllTextAsync(
        storePath,
        JsonSerializer.Serialize(recordEnvelope, jsonOptions));

    var durableBytes = await File.ReadAllBytesAsync(storePath);
    checks["plaintext_absent_from_durable_record"] = durableBytes
        .AsSpan()
        .IndexOf(Encoding.UTF8.GetBytes(PlaintextSentinel)) < 0;
    checks["authenticated_record_round_trip"] =
        recordEnvelope.Decrypt(dataKey) == PlaintextSentinel;

    var tampered = recordEnvelope with
    {
        Ciphertext = FlipFirstByte(recordEnvelope.Ciphertext),
    };
    checks["tampered_record_fails_closed"] = ThrowsCryptographicException(
        () => tampered.Decrypt(dataKey));

    File.Delete(storePath);
}
finally
{
    CryptographicOperations.ZeroMemory(dataKey);
}

var websocketResult = await RunLoopbackWebSocketProbeAsync();
checks["loopback_websocket_round_trip"] = websocketResult.RoundTrip;
checks["stop_cancels_pending_receive"] = websocketResult.StopCancelledReceive;
checks["stop_closes_socket"] = websocketResult.SocketClosed;

var station = new ProbeStation();
checks["launch_is_stopped_and_locked"] = station.State == StationState.StoppedLocked;
station.UnlockForProbe();
station.StartForProbe();
station.StopForProbe();
checks["stop_returns_to_locked_fail_closed_state"] =
    station.State == StationState.StoppedLocked && !station.ReconnectPermitted;

var recovered = ProbeStation.RecoverAfterUncleanTermination();
checks["unclean_restart_does_not_resume"] =
    recovered.State == StationState.StoppedLocked
    && recovered.CoverageGapDetected
    && !recovered.ReconnectPermitted;

notes.Add("The cryptographic passphrase is synthetic test data, not a user secret.");
notes.Add("The WebSocket probe uses loopback only and contacts no external endpoint.");
notes.Add("This console probe does not prove Android lifecycle, Keystore, notification, battery, or packaging behavior.");

var evidence = new
{
    generated_at_utc = DateTimeOffset.UtcNow,
    runtime = Environment.Version.ToString(),
    os = Environment.OSVersion.VersionString,
    architecture = System.Runtime.InteropServices.RuntimeInformation.ProcessArchitecture.ToString(),
    checks,
    all_passed = checks.Values.All(value => value),
    notes,
};

var evidencePath = ResolveEvidencePath();
await File.WriteAllTextAsync(
    evidencePath,
    JsonSerializer.Serialize(evidence, jsonOptions) + Environment.NewLine);

Console.WriteLine(JsonSerializer.Serialize(evidence, jsonOptions));
return evidence.all_passed ? 0 : 1;

static string FlipFirstByte(string encoded)
{
    var bytes = Convert.FromBase64String(encoded);
    bytes[0] ^= 0x01;
    return Convert.ToBase64String(bytes);
}

static bool ThrowsCryptographicException(Action action)
{
    try
    {
        action();
        return false;
    }
    catch (AuthenticationTagMismatchException)
    {
        return true;
    }
    catch (CryptographicException)
    {
        return true;
    }
}

static string ResolveEvidencePath()
{
    var current = new DirectoryInfo(AppContext.BaseDirectory);
    while (current is not null)
    {
        if (File.Exists(Path.Combine(current.FullName, "FoundationProbe.csproj")))
        {
            return Path.Combine(current.FullName, "probe-evidence.json");
        }

        current = current.Parent;
    }

    return Path.Combine(AppContext.BaseDirectory, "probe-evidence.json");
}

static async Task<WebSocketProbeResult> RunLoopbackWebSocketProbeAsync()
{
    using var listener = new TcpListener(IPAddress.Loopback, 0);
    listener.Start();
    var endpoint = (IPEndPoint)listener.LocalEndpoint;
    var acceptTask = listener.AcceptTcpClientAsync();

    using var clientTransport = new TcpClient(AddressFamily.InterNetwork);
    await clientTransport.ConnectAsync(IPAddress.Loopback, endpoint.Port);
    using var serverTransport = await acceptTask;

    using var clientSocket = WebSocket.CreateFromStream(
        clientTransport.GetStream(),
        isServer: false,
        subProtocol: null,
        keepAliveInterval: TimeSpan.FromSeconds(20));
    using var serverSocket = WebSocket.CreateFromStream(
        serverTransport.GetStream(),
        isServer: true,
        subProtocol: null,
        keepAliveInterval: TimeSpan.FromSeconds(20));

    var payload = Encoding.UTF8.GetBytes("bounded-loopback-signal");
    await serverSocket.SendAsync(
        new ArraySegment<byte>(payload),
        WebSocketMessageType.Text,
        endOfMessage: true,
        CancellationToken.None);

    var buffer = new byte[256];
    var receive = await clientSocket.ReceiveAsync(
        new ArraySegment<byte>(buffer),
        CancellationToken.None);
    var roundTrip = receive.EndOfMessage
        && receive.MessageType == WebSocketMessageType.Text
        && Encoding.UTF8.GetString(buffer, 0, receive.Count) == "bounded-loopback-signal";

    using var stop = new CancellationTokenSource();
    var pendingReceive = clientSocket.ReceiveAsync(
        new ArraySegment<byte>(buffer),
        stop.Token);
    stop.Cancel();

    var cancelled = false;
    try
    {
        await pendingReceive;
    }
    catch (OperationCanceledException)
    {
        cancelled = true;
    }

    clientSocket.Abort();
    serverSocket.Abort();
    listener.Stop();

    return new WebSocketProbeResult(
        roundTrip,
        cancelled,
        clientSocket.State is WebSocketState.Aborted or WebSocketState.Closed);
}

readonly record struct WebSocketProbeResult(
    bool RoundTrip,
    bool StopCancelledReceive,
    bool SocketClosed);

enum StationState
{
    StoppedLocked,
    ReadyUnlocked,
    Listening,
}

sealed class ProbeStation
{
    public StationState State { get; private set; } = StationState.StoppedLocked;

    public bool CoverageGapDetected { get; private init; }

    public bool ReconnectPermitted => State == StationState.Listening;

    public void UnlockForProbe()
    {
        if (State != StationState.StoppedLocked)
        {
            throw new InvalidOperationException("Unlock is allowed only from stopped and locked.");
        }

        State = StationState.ReadyUnlocked;
    }

    public void StartForProbe()
    {
        if (State != StationState.ReadyUnlocked)
        {
            throw new InvalidOperationException("Listening requires an unlocked station.");
        }

        State = StationState.Listening;
    }

    public void StopForProbe()
    {
        State = StationState.StoppedLocked;
    }

    public static ProbeStation RecoverAfterUncleanTermination() => new()
    {
        CoverageGapDetected = true,
    };
}

sealed record KeyEnvelope(
    int Iterations,
    string Salt,
    string Nonce,
    string Ciphertext,
    string Tag)
{
    private const int IterationCount = 210_000;
    private static readonly byte[] AssociatedData =
        Encoding.UTF8.GetBytes("csr-phase0b-key-envelope-v1");

    public static KeyEnvelope Create(string passphrase)
    {
        var salt = RandomNumberGenerator.GetBytes(16);
        var nonce = RandomNumberGenerator.GetBytes(12);
        var dataKey = RandomNumberGenerator.GetBytes(32);
        var wrappingKey = Rfc2898DeriveBytes.Pbkdf2(
            passphrase,
            salt,
            IterationCount,
            HashAlgorithmName.SHA256,
            32);
        var ciphertext = new byte[dataKey.Length];
        var tag = new byte[16];

        try
        {
            using var aes = new AesGcm(wrappingKey, tag.Length);
            aes.Encrypt(nonce, dataKey, ciphertext, tag, AssociatedData);
            return new KeyEnvelope(
                IterationCount,
                Convert.ToBase64String(salt),
                Convert.ToBase64String(nonce),
                Convert.ToBase64String(ciphertext),
                Convert.ToBase64String(tag));
        }
        finally
        {
            CryptographicOperations.ZeroMemory(wrappingKey);
            CryptographicOperations.ZeroMemory(dataKey);
        }
    }

    public bool TryUnwrap(string passphrase, out byte[] dataKey)
    {
        var salt = Convert.FromBase64String(Salt);
        var nonce = Convert.FromBase64String(Nonce);
        var ciphertext = Convert.FromBase64String(Ciphertext);
        var tag = Convert.FromBase64String(Tag);
        var wrappingKey = Rfc2898DeriveBytes.Pbkdf2(
            passphrase,
            salt,
            Iterations,
            HashAlgorithmName.SHA256,
            32);
        dataKey = new byte[ciphertext.Length];

        try
        {
            using var aes = new AesGcm(wrappingKey, tag.Length);
            aes.Decrypt(nonce, ciphertext, tag, dataKey, AssociatedData);
            return true;
        }
        catch (AuthenticationTagMismatchException)
        {
            CryptographicOperations.ZeroMemory(dataKey);
            dataKey = Array.Empty<byte>();
            return false;
        }
        finally
        {
            CryptographicOperations.ZeroMemory(wrappingKey);
        }
    }
}

sealed record RecordEnvelope(
    string Nonce,
    string Ciphertext,
    string Tag)
{
    private static readonly byte[] AssociatedData =
        Encoding.UTF8.GetBytes("csr-phase0b-record-v1");

    public static RecordEnvelope Encrypt(string plaintext, byte[] dataKey)
    {
        var nonce = RandomNumberGenerator.GetBytes(12);
        var plaintextBytes = Encoding.UTF8.GetBytes(plaintext);
        var ciphertext = new byte[plaintextBytes.Length];
        var tag = new byte[16];

        try
        {
            using var aes = new AesGcm(dataKey, tag.Length);
            aes.Encrypt(nonce, plaintextBytes, ciphertext, tag, AssociatedData);
            return new RecordEnvelope(
                Convert.ToBase64String(nonce),
                Convert.ToBase64String(ciphertext),
                Convert.ToBase64String(tag));
        }
        finally
        {
            CryptographicOperations.ZeroMemory(plaintextBytes);
        }
    }

    public string Decrypt(byte[] dataKey)
    {
        var nonce = Convert.FromBase64String(Nonce);
        var ciphertext = Convert.FromBase64String(Ciphertext);
        var tag = Convert.FromBase64String(Tag);
        var plaintext = new byte[ciphertext.Length];

        try
        {
            using var aes = new AesGcm(dataKey, tag.Length);
            aes.Decrypt(nonce, ciphertext, tag, plaintext, AssociatedData);
            return Encoding.UTF8.GetString(plaintext);
        }
        finally
        {
            CryptographicOperations.ZeroMemory(plaintext);
        }
    }
}
