import pytest

from taxestimator.webapp import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_index_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Federal Income Tax Estimator" in response.data


def test_estimate_happy_path(client):
    response = client.post(
        "/estimate",
        data={
            "tax_year": "2024",
            "filing_status": "single",
            "wages": "85000",
            "qualifying_children": "0",
        },
    )
    assert response.status_code == 200
    assert b"Total tax" in response.data
    assert b"10541.00" in response.data


def test_estimate_invalid_input_returns_400(client):
    response = client.post(
        "/estimate",
        data={
            "tax_year": "2024",
            "filing_status": "single",
            "wages": "-100",
        },
    )
    assert response.status_code == 400
