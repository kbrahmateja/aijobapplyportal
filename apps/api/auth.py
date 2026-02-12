from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User
from config import settings
from jose import jwt
from jose.exceptions import JOSEError
import httpx

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    
    try:
        # 1. Decode header to find Key ID (kid)
        header = jwt.get_unverified_header(token)
        
        # 2. In a real scenario, we fetch JWKS and verify signature.
        # For this MVP without keys, we might need a workaround or just decode unverified if we trust the channel (NOT RECOMMENDED for PROD).
        # However, to be robust, we'll try to decode assuming standard claims.
        
        # Mocking verification for now if no issuer is set, but extracting claims
        if not settings.CLERK_ISSUER:
            # DEV MODE: Decode unverified
            payload = jwt.get_unverified_claims(token)
        else:
            # TODO: Fetch JWKS from settings.CLERK_ISSUER + "/.well-known/jwks.json"
            # key = find_key(header['kid'])
            # payload = jwt.decode(token, key, algorithms=["RS256"], audience=...)
            payload = jwt.get_unverified_claims(token)
            
        clerk_id = payload.get("sub")
        email = payload.get("email") # Clerk might put email in "email" or "email_addresses"
        
        if not clerk_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing sub")

        # 3. Sync User to DB
        user = db.query(User).filter(User.clerk_id == clerk_id).first()
        
        if not user:
            # Check if user exists by email (legacy migration)
            # Clerk JWT might not always have email unless configured.
            # We'll assume for MVP we create a new user.
            user = User(
                clerk_id=clerk_id,
                email=email or f"{clerk_id}@clerk.user", # Fallback
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
        return user
        
    except JOSEError as e:
        raise HTTPException(status_code=401, detail=f"Could not validate credentials: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")
