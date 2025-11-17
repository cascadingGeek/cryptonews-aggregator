from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.payment import payment_service
from app.models.payment import PaymentTransaction
from app.database.session import AsyncSessionLocal
from datetime import datetime
from loguru import logger


class X402PaymentMiddleware(BaseHTTPMiddleware):
    """Middleware for handling X402 payment protocol"""
    
    # Endpoints that require payment
    PAID_ENDPOINTS = [
        "/markets/trends",
        "/markets/liquidity",
        "/markets/agents",
        "/markets/macro_events",
        "/markets/proof_of_work"
    ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request and verify payment if required"""
        
        # Check if endpoint requires payment
        if not any(request.url.path.startswith(endpoint) for endpoint in self.PAID_ENDPOINTS):
            return await call_next(request)
        
        # Get payment hash from header
        payment_hash = request.headers.get("X-Payment-Hash")
        
        if not payment_hash:
            # Return payment required response
            payment_headers = payment_service.get_payment_headers(request.url.path)
            return JSONResponse(
                status_code=402,
                content={
                    "error": "Payment Required",
                    "message": "This endpoint requires payment. Include X-Payment-Hash header.",
                    "payment_details": {
                        "amount": payment_service.price_per_request,
                        "currency": "USD",
                        "facilitator": payment_service.facilitator_url
                    }
                },
                headers=payment_headers
            )
        
        # Verify payment
        verification = await payment_service.verify_payment(payment_hash)
        
        if not verification.get("verified"):
            return JSONResponse(
                status_code=402,
                content={
                    "error": "Payment Verification Failed",
                    "message": verification.get("error", "Unable to verify payment"),
                    "payment_hash": payment_hash
                }
            )
        
        # Log payment transaction
        db = AsyncSessionLocal()
        try:
            transaction = PaymentTransaction(
                payment_hash=payment_hash,
                endpoint=request.url.path,
                amount=payment_service.price_per_request,
                verified=True,
                verified_at=datetime.utcnow(),
                user_identifier=request.client.host if request.client else None
            )
            db.add(transaction)
            db.commit()
            logger.info(f"Payment verified for {request.url.path}: {payment_hash[:16]}...")
        except Exception as e:
            logger.error(f"Error logging payment transaction: {str(e)}")
            db.rollback()
        finally:
            db.close()
        
        # Process request
        response = await call_next(request)
        
        # Settle payment after successful response
        if response.status_code == 200:
            settlement = await payment_service.settle_payment(
                payment_hash,
                payment_service.price_per_request
            )
            
            if settlement.get("settled"):
                # Update transaction
                db = AsyncSessionLocal()
                try:
                    transaction = db.query(PaymentTransaction).filter(
                        PaymentTransaction.payment_hash == payment_hash
                    ).first()
                    if transaction:
                        transaction.settled = True
                        transaction.settled_at = datetime.utcnow()
                        db.commit()
                except Exception as e:
                    logger.error(f"Error updating settlement: {str(e)}")
                    db.rollback()
                finally:
                    db.close()
        
        return response