import os
os.environ["DATABASE_URL"]="sqlite:///test.db"
from app import app
def test_health():
    r=app.test_client().get("/health")
    assert r.status_code==200
    assert r.json["status"]=="healthy"
