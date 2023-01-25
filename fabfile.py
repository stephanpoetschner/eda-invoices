import pathlib
import re
import string
import tempfile
from contextlib import contextmanager

import fabric
import invoke

remote_host = "flizz_app@opal5.opalstack.com"

remote_root = pathlib.PurePath("/home/flizz_app/")

remote_app = remote_root / "apps/flizz_app"
remote_app_port = "40575"

remote_src = remote_app / "flizz_app"
remote_venv = remote_root / "venv"
remote_etc = remote_root / "etc"
remote_tmp = remote_root / "tmp"
remote_logs = remote_root / "tmp" / "logs"

app_name = "eda_invoices"
app_settings = f"{app_name}.web.settings"
app_wsgi = f"{app_name}.wsgi"

local_root = pathlib.Path(__file__, "..").resolve().absolute()

default_template_ctx = {
    "contact_email": "stephan.poetschner@gmail.com",
    "sql_backup_user": "dummy",
    "$sql_backup_password": "dummy",
    "$sql_backup_database": "dummy",
}


@fabric.task
def bootstrap(ctx):
    conn = fabric.Connection(remote_host)

    # bootstrap environment
    bootstrap_directories(conn)
    bootstrap_venv(conn)
    verify_python(conn)
    bootstrap_poetry(conn)

    template_ctx = prepare_template_ctx()

    for binary_name in ["python", "gunicorn", "supervisord", "supervisorctl", "poetry"]:
        template_ctx[f"remote_binary_{binary_name}"] = str(_venv(binary_name))

    with local_clone() as local_clone_dir:
        for file_path in [
            "etc/gunicorn.conf",
            "etc/supervisord.conf",
            "etc/crontab.skel",
        ]:
            with open(local_clone_dir / file_path) as read_file:
                template = string.Template(read_file.read())
                data = template.substitute(**template_ctx)

            with open(local_clone_dir / file_path, "w") as write_file:
                write_file.write(data)

        invoke.run(
            "rsync --archive --verbose --compress"
            f"   {local_clone_dir}/etc/ {remote_host}:{remote_etc}",
            echo=True,
        )


@fabric.task
def deploy(ctx):
    conn = fabric.Connection(remote_host)

    with local_clone() as local_clone_dir:
        invoke.run(
            "rsync --archive --verbose --compress"
            "  --exclude .git"
            "  --exclude etc"
            f"  {local_clone_dir}/ {remote_host}:{remote_app}",
            echo=True,
        )

    # install steps
    base_path = remote_app / "src"

    with conn.cd(remote_app):
        conn.run(f'{_venv("poetry")} install --no-dev', echo=True)

    with conn.cd(base_path):
        # conn.run(f'{_venv("python")} manage.py migrate --settings={app_settings}', echo=True)
        conn.run(
            f'{_venv("python")} {app_name}/manage.py collectstatic --noinput'
            f" --settings={app_settings}",
            echo=True,
        )
        # conn.run(f'{_venv("python")} manage.py compilemessages --settings={app_settings}', echo=True)

    conn.run(
        f'{_venv("supervisorctl")} update &&   {_venv("supervisorctl")} restart all',
        echo=True,
    )


@contextmanager
def local_clone():
    with tempfile.TemporaryDirectory() as tmp_dirname:
        local_deploy_dir = pathlib.Path(tmp_dirname)
        invoke.run(f"git clone {local_root} {local_deploy_dir}", echo=True)
        invoke.run(
            f"cd {local_deploy_dir} && git rev-parse HEAD >"
            f" {local_deploy_dir / 'release.txt'}",
            echo=True,
        )
        yield local_deploy_dir


def _venv(cmd):
    return remote_venv / "bin" / cmd


def _create_secret_key(length):
    import random
    import string

    allowed_chars = "".join((string.ascii_letters, string.digits))
    return "".join(random.choice(allowed_chars) for _ in range(length))


def bootstrap_directories(conn):
    conn.run(f"mkdir --parent {remote_tmp}", echo=True)
    conn.run(f"mkdir --parent {remote_logs}", echo=True)


def bootstrap_venv(conn):
    result = conn.run(f"ls {remote_venv}", warn=True, echo=True)
    if result.failed:
        conn.run(f"python3 -m venv {remote_venv}", echo=True)


def verify_python(conn):
    result = conn.run(f'{_venv("python")} --version', warn=True, echo=True)
    if result.failed:
        print("No Python installed.")
        raise RuntimeError()

    major_version_re = re.compile(r"^Python (\d+)\.")
    matches = major_version_re.search(result.stdout or result.stderr)
    major_version = int(matches.groups()[0])
    if major_version <= 2:
        print("Python version>2 required.")
        raise RuntimeError()


def bootstrap_poetry(conn):
    result = conn.run(f'{_venv("poetry")} --version', warn=True, echo=True)
    if result.failed:
        conn.run(f'{_venv("pip")} install --upgrade pip', echo=True)
        conn.run(f'{_venv("pip")} install poetry', echo=True)

    conn.run(f'{_venv("poetry")} config virtualenvs.create false', echo=True)


def prepare_template_ctx(**kwargs):
    variables = dict(globals())
    ctx = {
        "django_secret": _create_secret_key(50),
    } | default_template_ctx

    ctx.update(
        {
            x: variables[x]
            for x in [
                "remote_root",
                "remote_app",
                "remote_app_port",
                "remote_src",
                "remote_etc",
                "remote_tmp",
                "remote_logs",
                "app_settings",
                "app_wsgi",
            ]
        }
    )
    ctx.update(kwargs)
    return ctx
