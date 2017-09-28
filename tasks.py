# -*- coding: utf-8 -*-
import sys
import os

from sys import platform
from os import environ
from pathlib import Path


from invoke import Collection, task


PROJECT_DIR = Path(__file__).parent


def walk_files(directory: Path):
    for _insider in directory.iterdir():
        if _insider.is_dir():
            subs = walk_files(_insider.resolve())
            for _sub in subs:
                yield _sub.resolve()
        else:
            yield _insider.resolve()


def find_all(glob):
    for f in walk_files(PROJECT_DIR):
        if glob in f.name:
            yield f


def yield_python_files(folder):
    for file in filter(lambda x: x.suffix == ".py", walk_files(folder)):
        yield file


@task
def pep8(ctx, folder=''):
    path = PROJECT_DIR / 'parsers' / folder
    for f in yield_python_files(path):
        print("Formatting", f)
        # FIXME: may use 'import autopep8' without console
        ctx.run("autopep8 --aggressive --aggressive --in-place {}".format(f))


@task
def clean(ctx):
    """Delete all compiled Python files"""
    for f in find_all(".pyc"):
        print("Removing", f)
        f.unlink()


@task
def lint(ctx, folder="parsers"):
    """Check style with flake8
       See more flake8 usage at:
           https://habrahabr.ru/company/dataart/blog/318776/
    """
    # E501 line too long
    # --max-line-length=100
    ctx.run('flake8 {} --exclude test* --ignore E501'.format(folder))


# documentation 


def apidoc(subpkg=None, exclude=''):
    """Call sphinx-apidoc to document *pkg* package without files
       in *exclude* pattern. """
    rst_source_dir = os.path.join('doc', 'rst')    
    pkg_dir = 'src'
    if subpkg is not None:
        pkg_dir = os.path.join('src', subpkg)
    flags = '--module-first --no-toc --force' 
    return f'sphinx-apidoc {flags} -o {rst_source_dir} {pkg_dir} {exclude}'


@task
def rst(ctx):
    """Build new rst files with sphinx-apidoc"""
    command = apidoc(exclude='*tests* *example*')
    ctx.run(command)


@task
def doc(ctx):
    source_dir = os.path.join('doc', 'rst')
    html_dir = os.path.join('doc', 'html')
    index_html = os.path.join(html_dir, 'index.html')
    build_command = f'sphinx-build -b html {source_dir} {html_dir}'
    ctx.run(build_command)
    if platform == "win32":
        ctx.run('start {}'.format(index_html))


@task
def find(ctx, regex):
    exclude = """ -name "*.py" ! -name "__init__.py" ! -name "test*" """
    command = ' | '.join([f"find . -type f {exclude}"
                        , f"xargs grep -nH '{regex}'"])
    ctx.run(command)
    

@task
def test(ctx):
    ctx.run("py.test parsers --doctest-modules")  # --cov=csv2df


@task
def cov(ctx):
    ctx.run("py.test --cov=parsers")
    ctx.run("coverage report --omit=*tests*,*__init__*")


@task
def ls(ctx):
    """List directory"""
    cmd = "dir /b"
    result = ctx.run(cmd, hide=False, warn=True)
    print(result.ok)
    print(result.stdout.splitlines())



ns = Collection()
for t in [ls, clean,
          pep8, lint,
          test, cov,
          doc, rst,
          find]:
    ns.add_task(t)


# Workaround for Windows execution
if platform == 'win32':
    # This is path to cmd.exe
    ns.configure({'run': {'shell': environ['COMSPEC']}})


if __name__ == '__main__':
    print(apidoc('', exclude='*test*'))