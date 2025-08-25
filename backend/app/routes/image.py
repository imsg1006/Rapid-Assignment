from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import ImageRequest
from app.dependencies import get_current_user, get_db
from app.models import ImageHistory, User
import mcp
from mcp.client.streamable_http import streamablehttp_client
import os
import logging
from dotenv import load_dotenv
import json

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

FLUX_API_URL = "https://server.smithery.ai/@falahgs/flux-imagegen-mcp-server/mcp?api_key=83d2480b-51ee-442b-82bd-a7f9b9fc198c&profile=considerable-sheep-UHo8NT"
API_KEY = os.getenv("FLUX_API_KEY")

async def generate_image(prompt: str):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="FLUX_API_KEY not found in .env")

    url = f"{FLUX_API_URL}?api_key={API_KEY}"
    logger.info(f"Connecting to Flux MCP at {url}")

    try:
        async with streamablehttp_client(url) as (read_stream, write_stream, _):
            async with mcp.ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools_result = await session.list_tools()

                if not tools_result.tools:
                    raise HTTPException(status_code=500, detail="No tools available from Flux MCP")

                tool_name = "generateImageUrl"
                result = await session.call_tool(
                    name=tool_name,
                    arguments={"prompt": prompt}
                )

                if not result or result.isError:
                    raise HTTPException(status_code=500, detail=f"No valid response from {tool_name}")

                if result.content and len(result.content) > 0 and hasattr(result.content[0], 'text'):
                    data = json.loads(result.content[0].text)
                    image_url = data.get("imageUrl")
                    if not image_url:
                        raise HTTPException(status_code=500, detail="No imageUrl in response")
                    return image_url
                else:
                    raise HTTPException(status_code=500, detail=f"No valid content from {tool_name}")

    except Exception as e:
        logger.exception("Exception in generate_image")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_image_endpoint(
    request: ImageRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    API endpoint to generate an image using Flux MCP and save the history for the authenticated user.
    """
    logger.info(f"Image generation request from user {user.username} (ID: {user.id}) for prompt: '{request.prompt}'")

    try:
        # Generate the image using your working Flux MCP code
        image_url = await generate_image(request.prompt)
        logger.info(f"Image generated successfully: {image_url}")

        # Save the history to the database
        new_entry = ImageHistory(
            prompt=request.prompt,
            image_url=image_url,
            user_id=user.id
        )
        
        logger.info(f"Creating image history entry for user {user.id}")
        db.add(new_entry)
        
        try:
            db.commit()
            db.refresh(new_entry)
            logger.info(f"Image history saved successfully with ID: {new_entry.id}")
        except Exception as commit_error:
            logger.error(f"Database commit failed: {commit_error}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save image history"
            )

        return {
            "message": "Image generated and saved successfully", 
            "image_url": image_url,
            "history_id": new_entry.id
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is (from generate_image function)
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error in image generation endpoint: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}"
        )