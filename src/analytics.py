import hashlib
import json
import platform
import subprocess
import sys

_DOMAIN   = "app.analytics"
_ENDPOINT = "https://pl.vialing.it/api/event"
_APP_URL  = "https://" + _DOMAIN + "/blender/gv_point_cloud_exporter"

# Subprocess minimale: riceve {"url", "payload", "headers"} come argomento JSON,
# fa la richiesta HTTP e termina. Nessuna logica aggiuntiva.
_SUBPROCESS_SCRIPT = (
    "import sys,json,urllib.request;"
    "a=json.loads(sys.argv[1]);"
    "req=urllib.request.Request(a['url'],data=json.dumps(a['payload']).encode(),"
    "headers=a['headers'],method='POST');"
    "urllib.request.urlopen(req,timeout=5)"
)

_hwid_cache: str | None = None


def _get_hwid() -> str:
    """
    Ritorna un identificatore hardware anonimizzato (SHA256, prime 16 cifre hex).
    Il valore viene calcolato una sola volta per sessione e poi messo in cache.
    """
    global _hwid_cache
    if _hwid_cache is not None:
        return _hwid_cache

    raw = None
    try:
        if sys.platform == "win32":
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Cryptography",
            )
            raw, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
        elif sys.platform == "darwin":
            out = subprocess.check_output(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                stderr=subprocess.DEVNULL,
                timeout=3,
            ).decode()
            for line in out.splitlines():
                if "IOPlatformUUID" in line:
                    raw = line.split('"')[-2]
                    break
        else:  # Linux
            for path in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
                try:
                    with open(path) as f:
                        raw = f.read().strip()
                    break
                except OSError:
                    pass
    except Exception:
        pass

    if not raw:
        raw = platform.node()  # fallback: hostname

    _hwid_cache = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return _hwid_cache


def _spawn(payload: dict, headers: dict) -> None:
    arg = json.dumps({"url": _ENDPOINT, "payload": payload, "headers": headers})
    kw = {
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }
    if sys.platform == "win32":
        kw["creationflags"] = subprocess.CREATE_NO_WINDOW
    subprocess.Popen([sys.executable, "-c", _SUBPROCESS_SCRIPT, arg], **kw)


def track(event_name: str, params: dict = None) -> None:
    """
    Invia un evento a Plausible se l'utente ha acconsentito.
    Deve essere chiamata dal thread principale di Blender.
    """
    try:
        import bpy
        if not bpy.app.online_access:
            return
        prefs = bpy.context.preferences.addons[__package__].preferences
        if not prefs.enable_analytics:
            return
        blender_version = ".".join(str(v) for v in bpy.app.version[:2])
    except Exception:
        return

    hwid = _get_hwid()
    payload = {
        "domain": _DOMAIN,
        "name":   event_name,
        "url":    _APP_URL,
        "props":  params or {},
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": f"BlenderAddon/{blender_version} GV-PointCloudExporter (hwid:{hwid})",
    }

    try:
        _spawn(payload, headers)
    except Exception:
        pass  # non bloccare mai l'addon per un errore di analytics
