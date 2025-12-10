import sys, hashlib, argparse
def hash(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(4096), b""): h.update(c)
    return "0x" + h.hexdigest()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["register", "verify"])
    parser.add_argument("file")
    args = parser.parse_args()
    print(f"Hash: {hash(args.file)}")
    print("Action Complete.")