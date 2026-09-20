from __future__ import annotations

import getpass
import json
import os
import sys
import urllib.parse
from pathlib import Path
from typing import Any

import requests
import urllib3


# ============================================================
# DEFAULTS
# ============================================================

DEFAULT_BASE_URL = "https://192.168.31.210:8443"
DEFAULT_VERIFY_TLS = False
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_SERVICE_ACCOUNT_NAME = "ansible-api"
DEFAULT_ENV_PATH = Path(__file__).resolve().parent / ".env"

# Linux: ssh/password
# Windows: winrm/password
DEFAULT_SECRET_PATHS = [
    "ansible/hosts/app-secrets/ssh/password",
    "ansible/hosts/soar-ir/ssh/password",
    "ansible/hosts/soc-wazuh/ssh/password",
    "ansible/hosts/win-server/winrm/password",
    "ansible/hosts/win10-endpoint/winrm/password",
    "ansible/hosts/ndr-sensor/ssh/password", 
]


# ============================================================
# ERRORS
# ============================================================

class ApiError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


# ============================================================
# INPUT HELPERS
# ============================================================

def ask_text(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    value = input(f"{prompt}{suffix}: ").strip()

    if value:
        return value

    if default is not None:
        return default

    raise ValueError(f"Required value is empty: {prompt}")


def ask_bool(prompt: str, default: bool) -> bool:
    default_text = "true" if default else "false"
    raw = ask_text(prompt, default_text).strip().lower()

    if raw in {"1", "true", "yes", "y", "да", "д"}:
        return True

    if raw in {"0", "false", "no", "n", "нет", "н"}:
        return False

    raise ValueError(f"Invalid boolean value: {raw}")


def ask_hidden(prompt: str) -> str:
    while True:
        value = getpass.getpass(f"{prompt}: ")
        if value:
            return value
        print("ERROR: value cannot be empty")


def ask_visible_secret(prompt: str, confirm: bool = True) -> str:
    """
    Значение секрета вводится с отображением в консоли.
    """
    while True:
        value = input(f"{prompt}: ").strip()

        if not value:
            print("ERROR: secret value cannot be empty")
            continue

        if not confirm:
            return value

        value2 = input(f"{prompt} again: ").strip()

        if value == value2:
            return value

        print("ERROR: values do not match, try again")


def validate_base_url(base_url: str) -> None:
    if not base_url.startswith(("http://", "https://")):
        raise ValueError(
            f"Invalid Secret Service URL: {base_url!r}. "
            "URL must start with http:// or https://"
        )


# ============================================================
# HTTP HELPERS
# ============================================================

def api_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{path}"


def request_json(
    method: str,
    path: str,
    *,
    base_url: str,
    verify_tls: bool,
    admin_token: str | None = None,
    api_key: str | None = None,
    json_body: dict[str, Any] | None = None,
    expected_status: int | tuple[int, ...] = (200,),
) -> dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Admin JWT token
    if admin_token:
        headers["Authorization"] = f"Bearer {admin_token}"

    # Service account API key
    if api_key:
        headers["X-API-Key"] = api_key

    response = requests.request(
        method=method,
        url=api_url(base_url, path),
        headers=headers,
        json=json_body,
        verify=verify_tls,
        timeout=20,
    )

    expected = expected_status if isinstance(expected_status, tuple) else (expected_status,)

    if response.status_code not in expected:
        raise ApiError(
            f"{method} {path} failed\n"
            f"Status: {response.status_code}\n"
            f"Response: {response.text}",
            status_code=response.status_code,
        )

    if not response.text:
        return {}

    try:
        return response.json()
    except ValueError:
        raise ApiError(
            f"{method} {path} returned non-JSON response:\n"
            f"{response.text}",
            status_code=response.status_code,
        )


# ============================================================
# API OPERATIONS
# ============================================================

def login_as_admin(
    base_url: str,
    verify_tls: bool,
    username: str,
    password: str,
) -> str:
    data = request_json(
        method="POST",
        path="/api/v1/auth/login",
        base_url=base_url,
        verify_tls=verify_tls,
        json_body={
            "username": username,
            "password": password,
        },
        expected_status=200,
    )

    token = data.get("access_token")

    if not token:
        raise ApiError("Login succeeded, but access_token was not found in response")

    return token


def create_service_account(
    base_url: str,
    verify_tls: bool,
    admin_token: str,
    service_account_name: str,
) -> dict[str, Any]:
    return request_json(
        method="POST",
        path="/api/v1/service-accounts",
        base_url=base_url,
        verify_tls=verify_tls,
        admin_token=admin_token,
        json_body={
            "name": service_account_name,
            "expires_at": None,
        },
        expected_status=(200, 201),
    )


def create_secret(
    base_url: str,
    verify_tls: bool,
    admin_token: str,
    secret_path: str,
    secret_value: str,
) -> dict[str, Any]:
    return request_json(
        method="POST",
        path="/api/v1/secrets",
        base_url=base_url,
        verify_tls=verify_tls,
        admin_token=admin_token,
        json_body={
            "path": secret_path,
            "value": secret_value,
        },
        expected_status=(200, 201),
    )


def rotate_secret(
    base_url: str,
    verify_tls: bool,
    admin_token: str,
    secret_path: str,
    secret_value: str,
) -> dict[str, Any]:
    encoded_path = urllib.parse.quote(secret_path, safe="/")

    return request_json(
        method="POST",
        path=f"/api/v1/secrets/{encoded_path}/versions",
        base_url=base_url,
        verify_tls=verify_tls,
        admin_token=admin_token,
        json_body={
            "value": secret_value,
        },
        expected_status=(200, 201),
    )


def grant_read_access(
    base_url: str,
    verify_tls: bool,
    admin_token: str,
    principal_id: str,
    secret_path: str,
) -> dict[str, Any]:
    return request_json(
        method="POST",
        path="/api/v1/policies",
        base_url=base_url,
        verify_tls=verify_tls,
        admin_token=admin_token,
        json_body={
            "secret_path": secret_path,
            "principal_id": principal_id,
            "capability": "read",
        },
        expected_status=(200, 201),
    )


def read_secret_as_service_account(
    base_url: str,
    verify_tls: bool,
    api_key: str,
    secret_path: str,
) -> dict[str, Any]:
    encoded_path = urllib.parse.quote(secret_path, safe="/")

    return request_json(
        method="GET",
        path=f"/api/v1/secrets/{encoded_path}",
        base_url=base_url,
        verify_tls=verify_tls,
        api_key=api_key,
        expected_status=200,
    )


# ============================================================
# METADATA SANITIZATION
# ============================================================

SENSITIVE_KEYS = {
    "value",
    "secret",
    "plaintext",
    "ciphertext",
    "encrypted_value",
    "decrypted_value",
    "password",
    "api_key",
    "access_token",
    "token",
}


def remove_sensitive_fields(obj: Any) -> Any:
    """
    Удаляет значения секретов из ответа перед выводом в консоль.
    Это нужно для финальной проверки: проверить чтение можно, но пароль не светить.
    """
    if isinstance(obj, dict):
        clean: dict[str, Any] = {}
        for key, value in obj.items():
            if key.lower() in SENSITIVE_KEYS:
                continue
            clean[key] = remove_sensitive_fields(value)
        return clean

    if isinstance(obj, list):
        return [remove_sensitive_fields(item) for item in obj]

    return obj


def print_metadata_only(secret_path: str, response_data: dict[str, Any]) -> None:
    clean = remove_sensitive_fields(response_data)

    print()
    print(f"--- metadata check: {secret_path} ---")
    print(json.dumps(clean, ensure_ascii=False, indent=2))


# ============================================================
# FILE HELPERS
# ============================================================

def write_or_update_env_file(
    env_path: Path,
    base_url: str,
    verify_tls: bool,
    api_key: str,
) -> None:
    content = (
        f'SECRET_SERVICE_URL="{base_url}"\n'
        f'SECRET_SERVICE_API_KEY="{api_key}"\n'
        f'SECRET_SERVICE_VERIFY_TLS="{str(verify_tls).lower()}"\n'
    )

    env_path.parent.mkdir(parents=True, exist_ok=True)

    if env_path.exists():
        overwrite = ask_bool(
            f"{env_path} already exists. Overwrite it",
            False,
        )

        if not overwrite:
            print(f"SKIP: .env was not modified: {env_path}")
            return

    fd = os.open(env_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)

    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)

    os.chmod(env_path, 0o600)
    print(f"  .env written: {env_path}")


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    print("=== Secret-backed Ansible multi-host bootstrap ===")
    print("This script creates or rotates secrets for up to 6 machines.")
    print("For each predefined path, you can choose whether to create/rotate it.")
    print("Secret values are VISIBLE in the console by design.")
    print("Admin password and API key input are hidden.")
    print()

    try:
        base_url = ask_text("Secret Service URL", DEFAULT_BASE_URL)
        validate_base_url(base_url)

        verify_tls = ask_bool("Verify TLS certificate", DEFAULT_VERIFY_TLS)

        if not verify_tls:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        has_existing_api_key = ask_bool(
            "Do you already have a service account API key",
            False,
        )

        existing_api_key: str | None = None
        principal_id: str | None = None
        service_account_name: str | None = None
        api_key_prefix = "unknown"

        if has_existing_api_key:
            print()
            print("Existing API key mode selected.")
            print("A new service account will NOT be created.")
            existing_api_key = ask_hidden("Existing service account API key")
            principal_id = ask_text(
                "Existing service account principal_id for read policy",
                None,
            )
            api_key = existing_api_key
        else:
            print()
            print("New service account mode selected.")
            print("A new service account and API key will be created.")
            service_account_name = ask_text(
                "Service account name",
                DEFAULT_SERVICE_ACCOUNT_NAME,
            )

        admin_username = ask_text("Admin username", DEFAULT_ADMIN_USERNAME)
        admin_password = ask_hidden("Admin password")

        env_path = Path(
            ask_text("Path to Ansible .env file", str(DEFAULT_ENV_PATH))
        ).expanduser()

        print()
        print("Predefined secret paths:")
        for path in DEFAULT_SECRET_PATHS:
            print(f"  - {path}")

        print()
        print("For each path, choose whether to create/rotate the secret.")
        print("Linux paths use ssh/password. Windows paths use winrm/password.")
        print()

        selected_secrets: dict[str, str] = {}

        for path in DEFAULT_SECRET_PATHS:
            do_create = ask_bool(f"Create or rotate secret at {path}", True)

            if not do_create:
                print(f"  skipped: {path}")
                continue

            print(f"  selected: {path}")
            secret_value = ask_visible_secret(f"Secret value for {path}", confirm=True)
            selected_secrets[path] = secret_value
            print()

        if not selected_secrets:
            raise ValueError("No secrets selected. Nothing to create or rotate.")

        print()
        print("[1/6] Login as admin...")
        admin_token = login_as_admin(
            base_url=base_url,
            verify_tls=verify_tls,
            username=admin_username,
            password=admin_password,
        )

        if has_existing_api_key:
            print("[2/6] Use existing service account API key...")
            print("  new service account creation skipped")
        else:
            print("[2/6] Create service account and API key...")
            service_account = create_service_account(
                base_url=base_url,
                verify_tls=verify_tls,
                admin_token=admin_token,
                service_account_name=service_account_name or DEFAULT_SERVICE_ACCOUNT_NAME,
            )

            principal_id = service_account["principal_id"]
            api_key = service_account["api_key"]
            api_key_prefix = service_account.get("api_key_prefix", "unknown")

        if not principal_id:
            raise ValueError(
                "principal_id is required to grant read policy to the service account"
            )

        created_or_rotated_paths: list[str] = []

        print("[3/6] Create or rotate selected secrets...")
        for path, value in selected_secrets.items():
            try:
                create_secret(
                    base_url=base_url,
                    verify_tls=verify_tls,
                    admin_token=admin_token,
                    secret_path=path,
                    secret_value=value,
                )
                print(f"  created: {path}")
                created_or_rotated_paths.append(path)

            except ApiError as exc:
                if exc.status_code != 409:
                    raise

                print(f"  already exists: {path}")
                do_rotate = ask_bool(f"Rotate/update existing secret at {path}", True)

                if do_rotate:
                    rotate_secret(
                        base_url=base_url,
                        verify_tls=verify_tls,
                        admin_token=admin_token,
                        secret_path=path,
                        secret_value=value,
                    )
                    print(f"  rotated: {path}")
                    created_or_rotated_paths.append(path)
                else:
                    print(f"  skipped rotation: {path}")

        if not created_or_rotated_paths:
            raise ValueError("No secrets were created or rotated.")

        print("[4/6] Grant read access to service account...")
        for path in created_or_rotated_paths:
            grant_read_access(
                base_url=base_url,
                verify_tls=verify_tls,
                admin_token=admin_token,
                principal_id=principal_id,
                secret_path=path,
            )
            print(f"  read policy: {path}")

        print("[5/6] Write/update Ansible .env file...")
        write_or_update_env_file(
            env_path=env_path,
            base_url=base_url,
            verify_tls=verify_tls,
            api_key=api_key,
        )

        print("[6/6] Verify created secrets using service account API key...")
        print("Only metadata will be printed. Secret values will be removed from output.")

        for path in created_or_rotated_paths:
            response_data = read_secret_as_service_account(
                base_url=base_url,
                verify_tls=verify_tls,
                api_key=api_key,
                secret_path=path,
            )
            print_metadata_only(path, response_data)

    except KeyboardInterrupt:
        print("\nERROR: interrupted", file=sys.stderr)
        return 130

    except (ApiError, OSError, ValueError, requests.RequestException) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print()
    print("DONE")

    if has_existing_api_key:
        print("Service account: existing")
    else:
        print(f"Service account name: {service_account_name}")
        print(f"API key prefix: {api_key_prefix}")

    print(f"Principal ID: {principal_id}")
    print(f"Env file: {env_path}")

    print()
    print("Created/rotated secret paths:")
    for path in created_or_rotated_paths:
        print(f"  - {path}")

    print()
    print("Do not commit .env to Git.")
    print("Do not commit this script if it contains temporary sensitive values.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
