# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.auth_service import auth_service
from app.schemas.auth_schemas import UserCreate, UserLogin, Token

router = APIRouter()

@router.post("/signup")
async def signup(user_credentials: UserCreate):
    """
    Create a new user.
    If email confirmation is enabled, it returns a message.
    If disabled, it returns a JWT token.
    """
    try:
        response = auth_service.get_supabase_client().auth.sign_up({
            "email": user_credentials.email,
            "password": user_credentials.password,
        })

        # Case 1: Email confirmation is required. User is created, but no session yet.
        if response.user and not response.session:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Signup successful. Please check your email to confirm your account."}
            )

        # Case 2: Signup is successful and a session is returned (auto-confirmation is on).
        if response.session and response.session.access_token:
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "access_token": response.session.access_token,
                    "token_type": "bearer"
                }
            )
        
        # Case 3: Unexpected response from Supabase.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not sign up user. Unexpected response from authentication service.",
        )

    except Exception as e:
        error_message = str(e)
        # Check for a common error message when user already exists.
        if 'User already registered' in error_message:
             raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        print(f"An error occurred during signup: {type(e).__name__} - {error_message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """
    Authenticate a user and return a JWT token.
    """
    try:
        # Sign in the user with Supabase
        session = auth_service.get_supabase_client().auth.sign_in_with_password({
            "email": user_credentials.email,
            "password": user_credentials.password,
        })
        
        if not session or not session.session or not session.session.access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials or token not provided.",
            )
            
        return {
            "access_token": session.session.access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        # This is a broad exception to catch the specific error from gotrue
        # and help identify the correct exception class.
        error_message = str(e)
        print(f"An error occurred during login: {type(e).__name__} - {error_message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message or "Invalid credentials",
        )
