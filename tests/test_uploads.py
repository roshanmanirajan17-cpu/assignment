import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src-election-system"))

from app import app


def test_uploaded_logo_is_served():
    client = app.test_client()
    response = client.get("/uploads/mila_logo.png")

    assert response.status_code == 200
    assert response.mimetype.startswith("image")
