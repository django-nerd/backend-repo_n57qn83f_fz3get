import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import User, Group, Message

app = FastAPI(title="Healthy Living Support API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Healthy Living Support API is running"}


# Utility to validate ObjectId strings

def validate_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")


# Users (minimal, for future extension)
@app.post("/api/users", response_model=dict)
def create_user(user: User):
    inserted_id = create_document("user", user)
    return {"id": inserted_id}


# Groups
@app.post("/api/groups", response_model=dict)
def create_group(group: Group):
    inserted_id = create_document("group", group)
    return {"id": inserted_id}


@app.get("/api/groups", response_model=List[dict])
def list_groups():
    groups = get_documents("group")
    # Convert ObjectId to string for frontend
    for g in groups:
        g["id"] = str(g.pop("_id"))
    return groups


# Messages
@app.post("/api/groups/{group_id}/messages", response_model=dict)
def post_message(group_id: str, message: Message):
    # Ensure the message is for the given group
    if message.group_id != group_id:
        raise HTTPException(status_code=400, detail="group_id mismatch")

    # Validate group exists
    gid = validate_object_id(group_id)
    group = db["group"].find_one({"_id": gid})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    inserted_id = create_document("message", message)
    return {"id": inserted_id}


@app.get("/api/groups/{group_id}/messages", response_model=List[dict])
def get_messages(group_id: str):
    gid = validate_object_id(group_id)
    msgs = list(db["message"].find({"group_id": str(gid)}).sort("created_at", 1))
    for m in msgs:
        m["id"] = str(m.pop("_id"))
    return msgs


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
