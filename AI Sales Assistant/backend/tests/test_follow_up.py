import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_process_message_single(client: AsyncClient):
    conv_id = "test-conv-123"
    response = await client.post(
        f"/conversations/{conv_id}/messages",
        json={"customer_message": "I need a phone under ₹22,000 with a good camera and battery."}
    )
    assert response.status_code == 200
    data = response.json()
    assert "intent" in data
    assert "requirements" in data
    assert "budget_max" in data["requirements"]
    
@pytest.mark.asyncio
async def test_process_message_empty(client: AsyncClient):
    conv_id = "test-conv-123"
    response = await client.post(
        f"/conversations/{conv_id}/messages",
        json={"customer_message": "   "}
    )
    assert response.status_code == 500 or response.status_code == 400

@pytest.mark.asyncio
async def test_follow_up_draft(client: AsyncClient):
    conv_id = "test-conv-123"
    response = await client.post(
        f"/conversations/{conv_id}/follow-up"
    )
    assert response.status_code == 200
    data = response.json()
    assert "draft_text" in data
