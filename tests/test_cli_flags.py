import subprocess
def test_cli_help():
    r = subprocess.run(["python3","-m","dexscreener_cli.cli","--help"], capture_output=True, timeout=5)
    assert r.returncode == 0
