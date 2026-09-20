from __future__ import annotations

import os
import urllib.parse
from pathlib import Path
from typing import Any

import requests
import urllib3

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase


def _parse_env_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _load_env_file() -> dict[str, str]:
    candidates = []

    explicit = os.getenv("SECRET_SERVICE_ENV_FILE")
    if explicit:
        candidates.append(Path(explicit).expanduser())

    # Usually Ansible is started from the repository ansible directory.
    candidates.append(Path.cwd() / ".env")

    # lookup_plugins/secret_service.py -> parent is ansible directory if layout is standard.
    candidates.append(Path(__file__).resolve().parent.parent / ".env")

    result: dict[str, str] = {}
    for path in candidates:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            result[key.strip()] = _parse_env_value(value)
        break
    return result


class LookupModule(LookupBase):
    """
    Read a secret value from the SOC-LAB Secret Management Service.

    Example:
      ansible_password: "{{ lookup('secret_service', 'ansible/hosts/app-secrets/ssh/password') }}"

    Configuration precedence (highest first):
      URL and TLS: kwargs, Ansible variables, environment, .env.
      API key: kwargs, environment, .env.
      API key header: kwargs, Ansible variables, .env, default.
      Read endpoint: kwargs, Ansible variables, default.

    The first available .env file is loaded from SECRET_SERVICE_ENV_FILE,
    the current directory, or the repository ansible directory.
    """

    def run(self, terms, variables=None, **kwargs):
        variables = variables or {}
        env_file_values = _load_env_file()

        base_url = (
            kwargs.get("base_url")
            or variables.get("secret_service_base_url")
            or os.getenv("SECRET_SERVICE_URL")
            or env_file_values.get("SECRET_SERVICE_URL")
        )

        api_key = (
            kwargs.get("api_key")
            or os.getenv("SECRET_SERVICE_API_KEY")
            or env_file_values.get("SECRET_SERVICE_API_KEY")
        )

        api_key_header = (
            kwargs.get("api_key_header")
            or variables.get("secret_service_api_key_header")
            or env_file_values.get("SECRET_SERVICE_API_KEY_HEADER")
            or "X-API-Key"
        )

        # Preserve an explicitly configured False instead of falling through.
        verify_tls_raw = next(
            (
                value
                for value in (
                    kwargs.get("verify_tls"),
                    variables.get("secret_service_verify_tls"),
                    os.getenv("SECRET_SERVICE_VERIFY_TLS"),
                    env_file_values.get("SECRET_SERVICE_VERIFY_TLS"),
                )
                if value is not None and value != ""
            ),
            False,
        )

        verify_tls = str(verify_tls_raw).lower() in {"1", "true", "yes", "y"}

        read_endpoint = (
            kwargs.get("read_endpoint")
            or variables.get("secret_service_read_endpoint")
            or "/api/v1/secrets/{path}"
        )

        if not base_url:
            raise AnsibleError("SECRET_SERVICE_URL is not set and .env was not found")
        if not api_key:
            raise AnsibleError("SECRET_SERVICE_API_KEY is not set and .env does not contain it")

        if not verify_tls:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        results = []
        for term in terms:
            secret_path = str(term).strip()
            if not secret_path:
                raise AnsibleError("Empty secret path was passed to secret_service lookup")

            encoded_path = secret_path
            endpoint = read_endpoint.format(path=encoded_path)
            url = f"{base_url.rstrip('/')}{endpoint}"

            headers = {
                "Accept": "application/json",
            }

            if api_key_header.lower() == "authorization":
                headers["Authorization"] = f"Bearer {api_key}"
            else:
                headers[api_key_header] = api_key

            try:
                response = requests.get(
                    url,
                    headers=headers,
                    verify=verify_tls,
                    timeout=15,
                )
            except requests.RequestException as exc:
                raise AnsibleError(f"Secret service request failed for {secret_path}: {exc}")

            if response.status_code != 200:
                raise AnsibleError(
                    f"Secret service returned {response.status_code} for {secret_path}: {response.text}"
                )

            try:
                data: dict[str, Any] = response.json()
            except ValueError as exc:
                raise AnsibleError(f"Secret service returned non-JSON response: {exc}")

            value = (
                data.get("value")
                or data.get("secret")
                or data.get("data", {}).get("value")
                or data.get("data", {}).get("secret")
            )
            if value is None:
                raise AnsibleError(
                    f"Secret value was not found in response for {secret_path}. "
                    "Expected one of: value, secret, data.value, data.secret."
                )

            results.append(str(value))

        return results
