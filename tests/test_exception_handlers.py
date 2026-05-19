"""
Tests for global exception handlers defined in app/core/exception.py.

Each handler is exercised by registering it on a minimal FastAPI app and
hitting a route that deliberately raises the corresponding exception.
"""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError as PydanticValidationError
from sqlalchemy.exc import SQLAlchemyError


# ---------------------------------------------------------------------------
# Helpers — build a fresh test app per handler
# ---------------------------------------------------------------------------

def make_app() -> FastAPI:
    """Return a minimal FastAPI app with all custom exception handlers registered."""
    from app.core.exception import (
        validation_exception_handler,
        http_exception_handler,
        database_exception_handler,
        general_exception_handler,
    )

    app = FastAPI()
    app.add_exception_handler(PydanticValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    return app


# ---------------------------------------------------------------------------
# 1. validation_exception_handler
# ---------------------------------------------------------------------------

class _SampleModel(BaseModel):
    age: int


class TestValidationExceptionHandler:
    """Handler for Pydantic ValidationError → 422 response."""

    @pytest.fixture(autouse=True)
    def setup(self):
        app = make_app()

        @app.get("/trigger-validation")
        def trigger_validation():
            # Deliberately construct an invalid model to raise ValidationError
            _SampleModel.model_validate({"age": "not-a-number"})

        self.client = TestClient(app, raise_server_exceptions=False)

    def test_returns_422_status_code(self):
        response = self.client.get("/trigger-validation")
        assert response.status_code == 422

    def test_response_contains_error_code(self):
        response = self.client.get("/trigger-validation")
        body = response.json()
        assert body["error_code"] == "VALIDATION_ERROR"

    def test_response_contains_message(self):
        response = self.client.get("/trigger-validation")
        body = response.json()
        assert body["message"] == "Validation failed"

    def test_response_contains_errors_list(self):
        response = self.client.get("/trigger-validation")
        body = response.json()
        assert "errors" in body
        assert isinstance(body["errors"], list)
        assert len(body["errors"]) > 0

    def test_response_contains_metadata_fields(self):
        response = self.client.get("/trigger-validation")
        body = response.json()
        assert "timestamp" in body
        assert "path" in body
        assert "request_id" in body


# ---------------------------------------------------------------------------
# 2. http_exception_handler
# ---------------------------------------------------------------------------

class TestHTTPExceptionHandler:
    """Handler for FastAPI HTTPException — covers dict detail, string detail, 4xx and 5xx."""

    @pytest.fixture(autouse=True)
    def setup(self):
        app = make_app()

        @app.get("/http-404-string")
        def raise_404_string():
            raise HTTPException(status_code=404, detail="not found")

        @app.get("/http-400-dict")
        def raise_400_dict():
            raise HTTPException(
                status_code=400,
                detail={"message": "bad request", "error_code": "BAD_INPUT"},
            )

        @app.get("/http-500-string")
        def raise_500_string():
            raise HTTPException(status_code=500, detail="server broke")

        self.client = TestClient(app, raise_server_exceptions=False)

    def test_404_returns_correct_status(self):
        response = self.client.get("/http-404-string")
        assert response.status_code == 404

    def test_string_detail_wrapped_in_message(self):
        response = self.client.get("/http-404-string")
        body = response.json()
        assert body["message"] == "not found"
        assert body["error_code"] == "HTTP_ERROR"

    def test_string_detail_contains_metadata(self):
        response = self.client.get("/http-404-string")
        body = response.json()
        assert "timestamp" in body
        assert "path" in body
        assert "request_id" in body

    def test_dict_detail_merged_into_response(self):
        response = self.client.get("/http-400-dict")
        assert response.status_code == 400
        body = response.json()
        assert body["message"] == "bad request"
        assert body["error_code"] == "BAD_INPUT"

    def test_dict_detail_contains_metadata(self):
        response = self.client.get("/http-400-dict")
        body = response.json()
        assert "timestamp" in body
        assert "path" in body
        assert "request_id" in body

    def test_500_returns_correct_status(self):
        response = self.client.get("/http-500-string")
        assert response.status_code == 500

    def test_500_string_detail_wrapped_in_message(self):
        response = self.client.get("/http-500-string")
        body = response.json()
        assert body["message"] == "server broke"


# ---------------------------------------------------------------------------
# 3. database_exception_handler
# ---------------------------------------------------------------------------

class TestDatabaseExceptionHandler:
    """Handler for SQLAlchemy errors → 500 with DATABASE_ERROR code."""

    @pytest.fixture(autouse=True)
    def setup(self):
        app = make_app()

        @app.get("/db-error")
        def trigger_db_error():
            raise SQLAlchemyError("connection refused")

        self.client = TestClient(app, raise_server_exceptions=False)

    def test_returns_500_status(self):
        response = self.client.get("/db-error")
        assert response.status_code == 500

    def test_error_code_is_database_error(self):
        response = self.client.get("/db-error")
        body = response.json()
        assert body["error_code"] == "DATABASE_ERROR"

    def test_response_message(self):
        response = self.client.get("/db-error")
        body = response.json()
        assert body["message"] == "Database operation failed"

    def test_response_contains_hint(self):
        response = self.client.get("/db-error")
        body = response.json()
        assert "hint" in body

    def test_response_contains_metadata(self):
        response = self.client.get("/db-error")
        body = response.json()
        assert "timestamp" in body
        assert "path" in body
        assert "request_id" in body


# ---------------------------------------------------------------------------
# 4. general_exception_handler
# ---------------------------------------------------------------------------

class TestGeneralExceptionHandler:
    """Catch-all handler for unexpected exceptions → 500 with INTERNAL_ERROR code."""

    @pytest.fixture(autouse=True)
    def setup(self):
        app = make_app()

        @app.get("/unexpected-error")
        def trigger_unexpected():
            raise RuntimeError("something went really wrong")

        self.client = TestClient(app, raise_server_exceptions=False)

    def test_returns_500_status(self):
        response = self.client.get("/unexpected-error")
        assert response.status_code == 500

    def test_error_code_is_internal_error(self):
        response = self.client.get("/unexpected-error")
        body = response.json()
        assert body["error_code"] == "INTERNAL_ERROR"

    def test_response_message(self):
        response = self.client.get("/unexpected-error")
        body = response.json()
        assert body["message"] == "An unexpected error occurred"

    def test_response_contains_metadata(self):
        response = self.client.get("/unexpected-error")
        body = response.json()
        assert "timestamp" in body
        assert "path" in body
        assert "request_id" in body
