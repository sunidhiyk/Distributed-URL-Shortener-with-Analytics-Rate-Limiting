def test_register_user(client):

    res = client.post(
        "/auth/register",
        json={
            "email": "test@gmail.com",
            "password": "password123"
        }
    )

    assert res.status_code == 201


def test_login_user(client):

    client.post(
        "/auth/register",
        json={
            "email": "test@gmail.com",
            "password": "password123"
        }
    )

    res = client.post(
        "/auth/login",
        json={
            "email": "test@gmail.com",
            "password": "password123"
        }
    )

    assert res.status_code == 200

    data = res.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):

    client.post(
        "/auth/register",
        json={
            "email": "test@gmail.com",
            "password": "password123"
        }
    )

    res = client.post(
        "/auth/login",
        json={
            "email": "test@gmail.com",
            "password": "wrongpassword"
        }
    )

    assert res.status_code == 403 



def test_get_current_user(client):

    # Register
    client.post(
        "/auth/register",
        json={
            "email": "test@gmail.com",
            "password": "password123"
        }
    )

    # Login
    login_res = client.post(
        "/auth/login",
        json={
            "email": "test@gmail.com",
            "password": "password123"
        }
    )

    token = login_res.json()["access_token"]

    # Call protected endpoint
    res = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert res.status_code == 200

    data = res.json()

    assert data["email"] == "test@gmail.com"