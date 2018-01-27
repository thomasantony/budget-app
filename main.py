"""
this is the "secret sauce" -- a single entry-point that resolves the
import dependencies.  If you're using blueprints, you can import your
blueprints here too.

then when you want to run your app, you point to main.py or `main.app`
"""

# Monkey patch json
from json import JSONEncoder

def _default(self, obj):
    if str(obj.__class__.__name__) == 'Decimal':
        return str(obj)
    else:
        return getattr(obj.__class__, "to_json", _default.default)(obj)

_default.default = JSONEncoder().default  # Save unmodified default.
JSONEncoder.default = _default # replacement

from app import app, db
app.run()
