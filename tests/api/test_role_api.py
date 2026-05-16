import pytest


class TestRoleAPI:

    async def test_create_role(self, client):
        response = await client.post("/api/v1/roles/", json={
            "name": "testrole",
            "description": "Test role"
        })
        assert response.status_code == 201
        assert response.json()["name"] == "testrole"

    async def test_create_role_duplicate(self, client):
        payload = {"name": "duprole", "description": "desc"}
        await client.post("/api/v1/roles/", json=payload)
        response = await client.post("/api/v1/roles/", json=payload)
        assert response.status_code == 409

    async def test_get_roles(self, client):
        await client.post("/api/v1/roles/", json={"name": "listrole"})
        response = await client.get("/api/v1/roles/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_role_by_id(self, client):
        create_resp = await client.post("/api/v1/roles/", json={"name": "getrole"})
        role_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/roles/{role_id}")
        assert response.status_code == 200
        assert response.json()["id"] == role_id

    async def test_get_role_not_found(self, client):
        response = await client.get("/api/v1/roles/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    async def test_delete_role(self, client):
        create_resp = await client.post("/api/v1/roles/", json={"name": "delrole"})
        role_id = create_resp.json()["id"]

        response = await client.delete(f"/api/v1/roles/{role_id}")
        assert response.status_code == 204
