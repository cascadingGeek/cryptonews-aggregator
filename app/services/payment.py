import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
from loguru import logger


class PaymentService:
    """Service for handling X402 payment verification and settlement"""
    
    def __init__(self):
        self.facilitator_url = f"https://{settings.FACILITATOR_URL}"
        self.price_per_request = settings.PAYMENT_PRICE_PER_REQUEST
        self.client = None
    
    async def initialize(self):
        """Initialize HTTP client"""
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("✓ Payment service initialized")
    
    async def verify_payment(self, payment_hash: str) -> Dict[str, Any]:
        """
        Verify payment with facilitator
        
        Args:
            payment_hash: The payment hash from X-Payment-Hash header
            
        Returns:
            Verification result with status and details
        """
        try:
            response = await self.client.post(
                f"{self.facilitator_url}/verify",
                json={"payment_hash": payment_hash}
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Payment verified: {payment_hash[:16]}...")
                return {
                    "verified": True,
                    "payment_hash": payment_hash,
                    "amount": data.get("amount"),
                    "data": data
                }
            else:
                logger.warning(f"Payment verification failed: {response.status_code}")
                return {
                    "verified": False,
                    "payment_hash": payment_hash,
                    "error": f"Verification failed with status {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Payment verification error: {str(e)}")
            return {
                "verified": False,
                "payment_hash": payment_hash,
                "error": str(e)
            }
    
    async def settle_payment(
        self, 
        payment_hash: str, 
        amount: float
    ) -> Dict[str, Any]:
        """
        Settle payment with facilitator
        
        Args:
            payment_hash: The payment hash
            amount: Amount to settle
            
        Returns:
            Settlement result
        """
        try:
            response = await self.client.post(
                f"{self.facilitator_url}/settle",
                json={
                    "payment_hash": payment_hash,
                    "amount": amount
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Payment settled: {payment_hash[:16]}...")
                return {
                    "settled": True,
                    "payment_hash": payment_hash,
                    "amount": amount,
                    "data": data
                }
            else:
                logger.warning(f"Payment settlement failed: {response.status_code}")
                return {
                    "settled": False,
                    "payment_hash": payment_hash,
                    "error": f"Settlement failed with status {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Payment settlement error: {str(e)}")
            return {
                "settled": False,
                "payment_hash": payment_hash,
                "error": str(e)
            }
    
    def get_payment_headers(self, endpoint: str) -> Dict[str, str]:
        """
        Generate payment headers for X402 protocol
        
        Args:
            endpoint: The API endpoint being accessed
            
        Returns:
            Headers dictionary with payment requirements
        """
        return {
            "X-Accepts-Payment": "true",
            "X-Payment-Required": "true",
            "X-Payment-Amount": str(self.price_per_request),
            "X-Payment-Currency": "USD",
            "X-Payment-Facilitator": self.facilitator_url,
            "X-Payment-Endpoint": endpoint
        }
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()


payment_service = PaymentService()