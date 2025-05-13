#stuff going inside router.py
############################




@router.get("v1/ask_alyf/get_message_history", response_model=List[MessageHistory])
async def get_message_history(
    provider_id: str = Depends(token_auth),
    member_id: Optional[str] = None,
    thread_id: Optional[str] = None
) -> List[MessageHistory]:
    """Get message history for a provider or provider+member combination"""
    return await get_message_history_data(provider_id, member_id, thread_id)




# stuff going inside schemas.py
##############################


class MessageHistory(BaseModel):
    message_id: str
    timestamp: datetime
    message_text: str
    ai_generated: bool
    thread_id: Optional[str] = None




# stuff going inside apc_apis.py
############################## 



async def get_message_history_data(provider_id: str, member_id: Optional[str] = None, thread_id: Optional[str] = None) -> List[MessageHistory]:
    """Get message history from Medulla service"""
    try:
        medulla_url = json.loads(AlyfSecretManagerUtility().get_secret("medulla_config")).get("url", {}).get(os.getenv('ENV', 'dev'))
        data = {
            "provider_id": provider_id,
            **({"member_id": member_id} if member_id else {}),
            **({"thread_id": thread_id} if thread_id else {})
        }
        
        response = requests.post(
            f"{medulla_url}/askalyf/get_message_history",
            json=data,
            timeout=60
        ).json()
        
        if not response: return []
        df = pd.DataFrame([response] if isinstance(response, dict) else response)
        return df.apply(lambda row: MessageHistory(
            message_id=str(row.get('message_id', '')),
            timestamp=row.get('timestamp', datetime.datetime.now()),
            message_text=str(row.get('message_text', '')),
            ai_generated=row.get('ai_generated', False),
            thread_id=str(row.get('thread_id', ''))
        ), axis=1).tolist()
    except Exception as e:
        ALYF_LOGGER.log("ERROR", f"Message history error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get message history")
    