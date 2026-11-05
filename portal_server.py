"""Запуск портала для тестов: временная база, миграции, учебные данные, сервер Django на порту 8101."""
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import urllib.request

PORT = int(os.environ.get("QA_PORT", "8101"))
BASE = "http://127.0.0.1:%d" % PORT


def portal_dir():
    """Папка с manage.py. По умолчанию репозиторий conference-django лежит рядом с этим."""
    env = os.environ.get("PORTAL_DIR")
    if env:
        return pathlib.Path(env)
    return pathlib.Path(__file__).resolve().parent.parent / "conference-django" / "portal"


class Portal:
    def __init__(self):
        self.dir = portal_dir()
        self.tmp = tempfile.mkdtemp(prefix="qa_portal_")
        self.env = dict(os.environ, PORTAL_DB=os.path.join(self.tmp, "test.sqlite3"), PYTHONUTF8="1")
        self.proc = None
        self.log = None

    def manage(self, *args):
        return subprocess.run([sys.executable, "manage.py", *args], cwd=self.dir, env=self.env,
                              capture_output=True, text=True, encoding="utf-8", check=True).stdout

    def start(self):
        self.manage("migrate")
        self.manage("seed")
        self.log = open(os.path.join(self.tmp, "server.log"), "wb")
        self.proc = subprocess.Popen([sys.executable, "manage.py", "runserver", "127.0.0.1:%d" % PORT, "--noreload"],
                                     cwd=self.dir, env=self.env, stdout=self.log, stderr=self.log)
        for _ in range(60):
            time.sleep(0.5)
            try:
                urllib.request.urlopen(BASE + "/", timeout=2)
                return
            except urllib.error.HTTPError:
                return
            except Exception:
                pass
        raise RuntimeError("портал не запустился, смотри " + os.path.join(self.tmp, "server.log"))

    def stop(self):
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        if self.log:
            self.log.close()
