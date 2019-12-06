import os

from invoke import task

CLOUDFORMATION_TEMPLATES_DIR = 'templates'


@task
def build(c, docs=False):
    for filename in os.listdir(CLOUDFORMATION_TEMPLATES_DIR):
        print("Building {file}".format(file=filename))
        os.system("python {base}/{file}".
                  format(base=CLOUDFORMATION_TEMPLATES_DIR, file=filename))
        print("\t-> Finished building {file}".format(file=filename))
