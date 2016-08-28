#!/usr/bin/env python2.7

import click
import subprocess
import sys


@click.command()
@click.option('--result-json', default='result.json')
@click.argument('devpi_endpoint')
@click.option('--devpi-username', envvar='DEVPI_USERNAME')
@click.option('--devpi-password', envvar='DEVPI_PASSWORD')
@click.option('--bitbucket-branch', envvar='BITBUCKET_BRANCH')
def run(result_json, devpi_endpoint, devpi_username, devpi_password,
        bitbucket_branch):
    try:
        subprocess.check_call(["tox", "-r", "--result-json", result_json])
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
            subprocess.check_call([
                "bumpversion", "dev",
                "--list",
                "--no-commit",
                "--new-version=$(python setup.py --version).dev$(date +%s)"],
                shell=True)
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
