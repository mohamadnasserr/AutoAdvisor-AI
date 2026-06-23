import base64
import binascii
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.db.database import get_db
from backend.app.models.db_models import DealerUser, Dealership
from backend.app.models.schemas import DealerUserProfile


PASSWORD_ALGORITHM = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 310_000
DEMO_DEALER_ACCOUNTS = (
    {
        "email": "beirut@autoadvisor.demo",
        "password": "demo123",
        "full_name": "Beirut Dealer Admin",
        "dealership_name": "Beirut Auto Hub",
    },
    {
        "email": "jounieh@autoadvisor.demo",
        "password": "demo123",
        "full_name": "Jounieh Dealer Admin",
        "dealership_name": "Cedar Motors",
    },
    {
        "email": "tripoli@autoadvisor.demo",
        "password": "demo123",
        "full_name": "Tripoli Dealer Admin",
        "dealership_name": "North Coast Motors",
    },
)

bearer_scheme = HTTPBearer(auto_error=False)


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )
    return "$".join(
        (
            PASSWORD_ALGORITHM,
            str(PASSWORD_ITERATIONS),
            _base64url_encode(salt),
            _base64url_encode(derived_key),
        )
    )


def verify_password(password: str, encoded_password: str) -> bool:
    try:
        algorithm, iterations, salt_value, expected_value = encoded_password.split("$", 3)
        if algorithm != PASSWORD_ALGORITHM:
            return False
        salt = _base64url_decode(salt_value)
        expected_key = _base64url_decode(expected_value)
        actual_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            int(iterations),
        )
        return secrets.compare_digest(actual_key, expected_key)
    except (binascii.Error, TypeError, ValueError):
        return False


def create_access_token(dealer_user: DealerUser) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(dealer_user.id),
        "dealership_id": dealer_user.dealership_id,
        "role": dealer_user.role,
        "iat": int(now.timestamp()),
        "exp": int(
            (now + timedelta(minutes=settings.dealer_jwt_expire_minutes)).timestamp()
        ),
    }
    header = {"alg": "HS256", "typ": "JWT"}
    encoded_header = _base64url_encode(
        json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    encoded_payload = _base64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = hmac.new(
        settings.dealer_jwt_secret.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    return f"{encoded_header}.{encoded_payload}.{_base64url_encode(signature)}"


def decode_access_token(token: str) -> dict:
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        expected_signature = hmac.new(
            settings.dealer_jwt_secret.encode("utf-8"),
            signing_input,
            hashlib.sha256,
        ).digest()
        supplied_signature = _base64url_decode(encoded_signature)
        if not secrets.compare_digest(expected_signature, supplied_signature):
            raise ValueError("Invalid token signature.")

        header = json.loads(_base64url_decode(encoded_header))
        payload = json.loads(_base64url_decode(encoded_payload))
        if header.get("alg") != "HS256" or header.get("typ") != "JWT":
            raise ValueError("Invalid token header.")
        if int(payload["exp"]) <= int(datetime.now(timezone.utc).timestamp()):
            raise ValueError("Token expired.")
        int(payload["sub"])
        return payload
    except (
        binascii.Error,
        KeyError,
        TypeError,
        UnicodeDecodeError,
        ValueError,
        json.JSONDecodeError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired dealer token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


def authenticate_dealer_user(
    db: Session,
    email: str,
    password: str,
) -> DealerUser | None:
    dealer_user = (
        db.query(DealerUser)
        .filter(DealerUser.email == email.strip().lower())
        .first()
    )
    if (
        dealer_user is None
        or not dealer_user.is_active
        or not verify_password(password, dealer_user.hashed_password)
    ):
        return None
    return dealer_user


def build_dealer_profile(dealer_user: DealerUser) -> DealerUserProfile:
    return DealerUserProfile(
        id=dealer_user.id,
        email=dealer_user.email,
        full_name=dealer_user.full_name,
        dealership_id=dealer_user.dealership_id,
        dealership_name=dealer_user.dealership.name,
        role=dealer_user.role,
    )


def get_current_dealer_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> DealerUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Dealer authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    dealer_user = (
        db.query(DealerUser)
        .filter(DealerUser.id == int(payload["sub"]))
        .first()
    )
    if dealer_user is None or not dealer_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Dealer account is unavailable.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if dealer_user.dealership_id != int(payload["dealership_id"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Dealer token no longer matches this account.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return dealer_user


def seed_demo_dealer_users(db: Session) -> tuple[int, int]:
    inserted = 0
    updated = 0

    for account in DEMO_DEALER_ACCOUNTS:
        dealership = (
            db.query(Dealership)
            .filter(Dealership.name == account["dealership_name"])
            .first()
        )
        if dealership is None:
            continue

        dealer_user = (
            db.query(DealerUser)
            .filter(DealerUser.email == account["email"])
            .first()
        )
        if dealer_user is None:
            dealer_user = DealerUser(
                dealership_id=dealership.id,
                email=account["email"],
                hashed_password=hash_password(account["password"]),
                full_name=account["full_name"],
                role="dealer_admin",
                is_active=True,
            )
            db.add(dealer_user)
            inserted += 1
            continue

        changed = False
        if dealer_user.dealership_id != dealership.id:
            dealer_user.dealership_id = dealership.id
            changed = True
        if dealer_user.full_name != account["full_name"]:
            dealer_user.full_name = account["full_name"]
            changed = True
        if dealer_user.role != "dealer_admin" or not dealer_user.is_active:
            dealer_user.role = "dealer_admin"
            dealer_user.is_active = True
            changed = True
        if not verify_password(account["password"], dealer_user.hashed_password):
            dealer_user.hashed_password = hash_password(account["password"])
            changed = True
        if changed:
            updated += 1

    db.commit()
    return inserted, updated
