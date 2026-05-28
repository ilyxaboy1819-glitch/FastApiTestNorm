import pytest


class TestUserAPI:

    async def test_create_user(self, client):
        response = await client.post("/api/v1/users/", json={
            "username": "apiuser",
            "email": "apiuser@example.com",
            "full_name": "API User",
            "profile": {"bio": "hello"}
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "apiuser"
        assert data["profile"]["bio"] == "hello"

    async def test_create_user_duplicate(self, client):
        payload = {
            "username": "dupuser",
            "email": "dup@example.com",
            "profile": {"bio": "bio"}
        }
        await client.post("/api/v1/users/", json=payload)
        response = await client.post("/api/v1/users/", json=payload)
        assert response.status_code == 409

    async def test_get_users(self, client):
        await client.post("/api/v1/users/", json={
            "username": "listuser",
            "email": "list@example.com",
            "profile": {"bio": "bio"}
        })
        response = await client.get("/api/v1/users/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_user_by_id(self, client):
        create_resp = await client.post("/api/v1/users/", json={
            "username": "getuser",
            "email": "getuser@example.com",
            "profile": {"bio": "bio"}
        })
        user_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["id"] == user_id

    async def test_get_user_not_found(self, client):
        response = await client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    async def test_update_user(self, client):
        create_resp = await client.post("/api/v1/users/", json={
            "username": "updateuser",
            "email": "update@example.com",
            "profile": {"bio": "old"}
        })
        user_id = create_resp.json()["id"]

        response = await client.put(f"/api/v1/users/{user_id}", json={
            "username": "updated",
            "email": "updated@example.com"
        })
        assert response.status_code == 200
        assert response.json()["username"] == "updated"

    async def test_delete_user(self, client):
        create_resp = await client.post("/api/v1/users/", json={
            "username": "deluser",
            "email": "del@example.com",
            "profile": {"bio": "bio"}
        })
        user_id = create_resp.json()["id"]

        response = await client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 204
