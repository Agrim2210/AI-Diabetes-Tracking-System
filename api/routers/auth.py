from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.core.dependencies import get_db, get_current_user
from api.core.security import hash_password, verify_password, create_access_token
from api.core.exceptions import ConflictException, CredentialsException
from api.db import models
from api.schemas.auth import UserCreate, UserOut, Token

router = APIRouter(prefix="/auth", tags=["Auth"])


# ── Register ──────────────────────────────────────────────────────────────────

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.
    - Raises 409 if username or email already exists.
    """
    # Check duplicate username
    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise ConflictException("Username already taken.")

    # Check duplicate email
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise ConflictException("Email already registered.")

    user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate with username + password.
    Returns a JWT access token on success.
    OAuth2PasswordRequestForm sends data as form fields (not JSON).
    """
    user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise CredentialsException("Incorrect username or password.")

    if not user.is_active:
        raise CredentialsException("Account is inactive.")

    token = create_access_token(data={"sub": user.username})
    return Token(access_token=token)


# ── Get Current User (me) ─────────────────────────────────────────────────────

@router.get("/me", response_model=UserOut)
def get_me(current_user: models.User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user


# ── Logout ────────────────────────────────────────────────────────────────────

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(current_user: models.User = Depends(get_current_user)):
    """
    Logout endpoint.
    JWT is stateless — true invalidation requires a token blocklist.
    For now this signals the frontend to delete the stored token.
    Extend with a Redis or DB blocklist if needed.
    """
    return {"message": f"User '{current_user.username}' logged out successfully."}