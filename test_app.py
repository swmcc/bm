import os
import json
import pytest
import requests
from click.testing import CliRunner
from app import search_command, AUTH_TOKEN_FILE


@pytest.fixture(autouse=True)
def mock_env_variables(monkeypatch):
    monkeypatch.setenv('API_EMAIL', 'example@example.com')
    monkeypatch.setenv('API_PASSWORD', 'password')


def test_search_command_success(monkeypatch):
    mock_auth_token = 'mocked-auth-token'
    mock_response = "[{'active': True, 'created_at': '2022-03-11T06:23:57.240Z', 'id': 14, 'page': 'https://www.gitbook.com/book/codegangsta/building-web-apps-with-go/details', 'title': 'Building Web Apps', 'updated_at': '2022-03-11T06:23:57.240Z'}]"

    def mock_post(*args, **kwargs):
        return MockResponse(200, {'token': mock_auth_token})

    def mock_get(*args, **kwargs):
        if 'Authentication' in kwargs['headers'] and kwargs['headers']['Authentication'] == mock_auth_token:
            return MockResponse(200, mock_response)
        return MockResponse(401, {})

    monkeypatch.setattr(requests, 'post', mock_post)
    monkeypatch.setattr(requests, 'get', mock_get)

    runner = CliRunner()
    result = runner.invoke(search_command, ['--search', 'example'])
    links = json.dumps(mock_response, indent=4, sort_keys=True)
    assert result.exit_code == 0
    assert json.loads(links) == mock_response

def test_search_command_unauthorized(monkeypatch):
    mock_auth_token = 'mocked-auth-token'

    def mock_post(*args, **kwargs):
        return MockResponse(401, {})

    monkeypatch.setattr(requests, 'post', mock_post)

    runner = CliRunner()
    result = runner.invoke(search_command, ['-s', 'example'])

    assert result.exit_code == 0
    assert 'Authorisation failed' in result.output


class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        print(self.json_data)
        return self.json_data


@pytest.fixture(autouse=True)
def cleanup_auth_token_file():
    yield
    if os.path.exists(AUTH_TOKEN_FILE):
        os.remove(AUTH_TOKEN_FILE)
