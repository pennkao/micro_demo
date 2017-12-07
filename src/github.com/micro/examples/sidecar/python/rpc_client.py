import requests
import json
import sidecar

def main():
    response = sidecar.rpc_call("/greeter/say/hello", {"name": "John"})
    print response

if __name__ == "__main__":
    main()
