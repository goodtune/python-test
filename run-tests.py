#!/usr/bin/env python2.7

import click
import ConfigParser
import subprocess
import sys
import time


@click.command()
@click.option('--result-json', default='result.json')
@click.argument('devpi_endpoint')
@click.option('--devpi-username', envvar='DEVPI_USERNAME')
@click.option('--devpi-password', envvar='DEVPI_PASSWORD')
@click.option('--bitbucket-branch', envvar='BITBUCKET_BRANCH')
@click.option('--detox', is_flag=True)
@click.option(
    '--tox-ini-file', 'toxini', default='tox.ini', envvar='TOXINI',
    type=click.Path(exists=True, dir_okay=False, writable=True))
@click.option(
    '--work-dir', default='.tox', envvar='TOXWORKDIR',
    type=click.Path(file_okay=False, writable=True, resolve_path=True),
    help='Directory where tox will create virtual environments')
def run(result_json, devpi_endpoint, devpi_username, devpi_password,
        bitbucket_branch, detox, work_dir, toxini):
    config = ConfigParser.SafeConfigParser()
    config.read([toxini])

    if work_dir:
        config.set('tox', 'toxworkdir', work_dir)

    with open(toxini, 'w') as fp:
        config.write(fp)

    try:
        cmd = "detox" if detox else "tox"
        subprocess.check_call(["tox", "--showconfig"])
        subprocess.check_call([cmd, "-r", "--result-json", result_json])
    except subprocess.CalledProcessError:
        sys.exit(1)

    try:
        subprocess.check_call(["devpi", "use", devpi_endpoint])
    except subprocess.CalledProcessError:
        sys.exit(2)

    try:
        subprocess.check_call([
            "devpi", "login", devpi_username, "--password", devpi_password])
    except subprocess.CalledProcessError:
        sys.exit(3)

    if bitbucket_branch != 'master':
        try:
            version = subprocess.check_output([
                "python", "setup.py", "--version"]).strip()
            epoch = int(time.time())

            subprocess.check_call([
                "bumpversion",
                "--list",
                "--no-commit",
                "--new-version",
                "{}.dev{}".format(version, epoch),
                "dev"])
        except subprocess.CalledProcessError:
            sys.exit(4)

    try:
        subprocess.check_call(["devpi", "upload", "--no-vcs"])
    except subprocess.CalledProcessError:
        sys.exit(5)

    try:
        name, version = subprocess.check_output([
            sys.executable, "setup.py", "--name", "--version"]).split()
    except subprocess.CalledProcessError:
        sys.exit(6)

    try:
        devpi_list = subprocess.check_output([
            "devpi", "list", name + b"==" + version]).split()[0]
    except subprocess.CalledProcessError:
        sys.exit(7)

    try:
        subprocess.check_call([
            "curl", "-X", "POST", "--data-binary", "@result.json", devpi_list])
    except subprocess.CalledProcessError:
        sys.exit(8)


if __name__ == '__main__':
    run()
