
# Updated routes/search.py with debugging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_db
from app.models import SearchHistory, User
from duckduckgo_search import DDGS
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["search"])

@router.get("/")
async def search(
    query: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Performs a web search using DuckDuckGo, returns the results,
    and saves the search history for the authenticated user.
    """
    logger.info(f"Search request from user {user.username} (ID: {user.id}) for query: '{query}'")
    
    try:
        ddgs = DDGS()
        # Get a maximum of 5 search results
        results = list(ddgs.text(query, max_results=5))
        logger.info(f"DuckDuckGo search returned {len(results)} results")
        
        # Convert the list of results to a JSON string for database storage
        results_json = json.dumps(results)

        # Save the search history to the database
        new_entry = SearchHistory(
            query=query,
            results=results_json,
            user_id=user.id
        )
        
        logger.info(f"Creating search history entry for user {user.id}")
        db.add(new_entry)
        
        try:
            db.commit()
            db.refresh(new_entry)
            logger.info(f"Search history saved successfully with ID: {new_entry.id}")
        except Exception as commit_error:
            logger.error(f"Database commit failed: {commit_error}")
            db.rollback()
            raise

        return {"query": query, "results": results, "history_id": new_entry.id}
        
    except Exception as e:
        # Rollback the session in case of an error to prevent inconsistent state
        logger.error(f"Search operation failed: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during search: {e}"
        )

