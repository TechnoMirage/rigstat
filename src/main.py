import json
from exceptions import ApiAuthError, ApiConnectionError, ApiError
from monero import XMRigApi


def run_sync() -> None:
    ip = input("ip : ").strip()

    while True:
        port_input = input("port : ").strip()
        try:
            port = int(port_input)
            break
        except ValueError:
            print("Error : port must be a valid integer.")

    token_input = input("token : ").strip()
    access_token = token_input if token_input else None

    print(f"\nConnexion to http://{ip}:{port}/2/summary ...")
    client = XMRigApi(ip=ip, port=port, access_token=access_token)

    try:
        summary = client.get_summary()
        print("\n=== Data ===")
        print(json.dumps(summary, indent=2))
    except ApiConnectionError as err:
        print(f"\n[ERROR CONNEXION] {err}")
    except ApiAuthError as err:
        print(f"\n[ERROR AUTH] {err}")
    except ApiError as err:
        print(f"\n[ERROR API] {err}")


if __name__ == "__main__":
    run_sync()
