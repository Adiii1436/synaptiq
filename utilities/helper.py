def optional_import(name, attr=None):
    try:
        module = __import__(name, fromlist=[attr] if attr else [])
        return getattr(module, attr) if attr else module
    except ImportError:
        return None