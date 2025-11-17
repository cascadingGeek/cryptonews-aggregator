from fastapi import APIRouter, HTTPException
from app.controllers.markets_controller import MarketsController

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("/trends")
async def get_trends():
    """
    Get trending crypto news and social updates
    
    Returns:
        Merged data from CryptoNews API and Twitter feeds for trending topics
    """
    try:
        return await MarketsController.get_trends()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/liquidity")
async def get_liquidity():
    """
    Get liquidity-related crypto news and updates
    
    Returns:
        Merged data about trading volume, liquidity pools, and DEX activity
    """
    try:
        return await MarketsController.get_liquidity()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def get_agents():
    """
    Get AI agents and automation-related news
    
    Returns:
        Merged data about AI agents, bots, and automation in crypto
    """
    try:
        return await MarketsController.get_agents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/macro_events")
async def get_macro_events():
    """
    Get macro economic events and regulatory news
    
    Returns:
        Merged data about regulations, institutional adoption, and macro events
    """
    try:
        return await MarketsController.get_macro_events()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proof_of_work")
async def get_proof_of_work():
    """
    Get mining and Proof of Work related news
    
    Returns:
        Merged data about mining, hashrate, and PoW developments
    """
    try:
        return await MarketsController.get_proof_of_work()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))