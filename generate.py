import sys
import importlib

API="https://api-vigilo.jesuisundesdeux.org"
TEMPLATE = "parodie_stop_incivilite_montpellier"
TEMPLATEDIR = f"templates/{TEMPLATE}"
ISSUE_PICTURE="lodeve.png"

def loadTemplate(templatename):
    module = importlib.import_module(f'templates.{templatename}')
    moduleClass = getattr(module, f"TPL{templatename}")
    return moduleClass()

test = loadTemplate(TEMPLATE)
test.generate(API,ISSUE_PICTURE)
