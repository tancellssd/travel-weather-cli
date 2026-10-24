from travel import get_description, get_weather, get_info, get_currency, get_location
from unittest.mock import Mock
import travel as tl 
import requests

def test_get_description():
    assert get_description(0) == "Clear sky"
    assert get_description(3) == "Overcast"
    assert get_description(65) == "Heavy rain"

def test_unknown_weather_code():
    assert get_description(999) == "Unknown weather condition"

def test_get_currency_success(monkeypatch):
    fake_response = Mock()
    fake_response.json.return_value = {"rate": 0.92}

    monkeypatch.setattr(
        tl.requests,
        "get",
        lambda *args, **kwargs: fake_response
    )

    result = tl.get_currency("EUR")
    assert result is not None
    assert result == {"rate": 0.92}


def test_get_currency_timeout(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.exceptions.Timeout

    monkeypatch.setattr(tl.requests, "get", fake_get)

    assert tl.get_currency("EUR") is None

def test_get_location_success(monkeypatch):
    fake_response = Mock()
    fake_response.json.return_value = {
        "results": [
            {
                "name": "Nairobi",
                "country": "Kenya",
                "country_code": "KE",
                "latitude": -1.29,
                "longitude": 36.82
            }
        ]
    }

    monkeypatch.setattr(
        tl.requests,
        "get",
        lambda *args, **kwargs: fake_response
    )

    result = tl.get_location("Nairobi")

    assert result is not None
    assert result["results"][0]["name"] == "Nairobi"
    assert result["results"][0]["country_code"] == "KE"
    assert result["results"][0]["latitude"] == -1.29

#Tests response for unknown location
def test_get_location_not_found(monkeypatch):
    fake_response = Mock()
    fake_response.json.return_value = {"results": []}

    monkeypatch.setattr(
        tl.requests,
        "get",
        lambda *args, **kwargs: fake_response
    )

    result = tl.get_location("Unknownplacexyz")
    assert result is not None
    assert result["results"] == []

def test_get_location_timeout(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.exceptions.Timeout

    monkeypatch.setattr(tl.requests, "get", fake_get)
    assert tl.get_location("Nairobi") is None

def test_get_weather_success(monkeypatch):
    fake_response = Mock()
    fake_response.json.return_value = {
        "timezone": "Africa/Nairobi", 
        "current": {
            "temperature_2m": 25.0,
            "weather_code": 0,
            "time": "2026-10-20T15:00",
        },
    }

    monkeypatch.setattr(
        tl.requests,
        "get",
        lambda *args, **kwargs: fake_response
    )
    result = tl.get_weather(-1.29, 36.82)

    assert result is not None
    assert result["timezone"] == "Africa/Nairobi"
    assert result["current"]["temperature_2m"] == 25.0
    assert result["current"]["weather_code"] == 0

def test_get_weather_connection_error(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.exceptions.ConnectionError
    
    monkeypatch.setattr(tl.requests, "get", fake_get)
    assert tl.get_weather(-1.29, 36.82) is None

def test_get_weather_empty_response(monkeypatch):
    fake_response = Mock()
    fake_response.json.return_value = {}

    monkeypatch.setattr(tl.requests, "get", lambda *args, **kwargs: fake_response)
    result = tl.get_weather(-1.29, 36.82)
    assert result == {}

def test_get_info_success(monkeypatch):
    fake_response = Mock()
    fake_response.json.return_value = {
        "region": "Africa",
        "languages": [
            {"name": "Swahili"},
            {"name": "English"},
        ],
        "currencies": [
            {"code": "KES", "name": "Kenyan shilling"}
        ],
    }

    monkeypatch.setattr(
        tl.requests,
        "get",
        lambda *args, **kwargs: fake_response
    )
    result = tl.get_info("KE")

    assert result is not None
    assert result["region"] == "Africa"
    assert result["currencies"][0]["code"] == "KES"

def test_get_info_missing_country_code():
    assert tl.get_info(None) is None

def test_get_info_http_error(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.exceptions.HTTPError("Server error")

    monkeypatch.setattr(tl.requests, "get", fake_get)
    assert tl.get_info("KE") is None

def test_get_currency_http_error(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.exceptions.HTTPError("Server error")

    monkeypatch.setattr(tl.requests, "get", fake_get)
    assert tl.get_currency("EUR") is None

def test_get_currency_connection_error(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.exceptions.ConnectionError

    monkeypatch.setattr(tl.requests, "get", fake_get)
    assert tl.get_currency("EUR") is None

#Checks JSON format received from currency API is in a valid
def test_json_response(monkeypatch):
    fake_response = Mock()
    fake_response.json.side_effect = ValueError("Invalid JSON")

    monkeypatch.setattr(
        tl.requests,
        "get",
        lambda *args, **kwargs: fake_response
    )

    assert tl.get_currency("EUR") is None

#Checks JSON format received from currency API is in a valid specific structure
def test_get_currency_missing_rate(monkeypatch):
    fake_response = Mock()
    fake_response.json.return_value = {
        "message": "Currency not supported"
    }

    monkeypatch.setattr(
        tl.requests,
        "get",
        lambda *args, **kwargs: fake_response
    )

    result = tl.get_currency("EUR")
    assert result == {"message": "Currency not supported"}