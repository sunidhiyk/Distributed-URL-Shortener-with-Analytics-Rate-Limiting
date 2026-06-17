def create_user_and_get_token(client):

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

    return res.json()["access_token"]


def test_create_short_url(client):

    token = create_user_and_get_token(client)

    res = client.post(
        "/urls/shorten",
        json={
            "original_url": "https://google.com"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert res.status_code == 200

    data = res.json()

    assert data["original_url"] == "https://google.com/"
    assert "short_code" in data


def test_create_custom_alias(client):

    token = create_user_and_get_token(client)

    res = client.post(
        "/urls/shorten",
        json={
            "original_url": "https://github.com",
            "custom_alias": "github"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert res.status_code == 200

    data = res.json()

    assert data["short_code"] == "github"


def test_duplicate_alias(client):

    token = create_user_and_get_token(client)

    client.post(
        "/urls/shorten",
        json={
            "original_url": "https://github.com",
            "custom_alias": "github"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    res = client.post(
        "/urls/shorten",
        json={
            "original_url": "https://google.com",
            "custom_alias": "github"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert res.status_code == 400  



def test_get_my_urls(client):

    token = create_user_and_get_token(client)

    client.post(
        "/urls/shorten",
        json={
            "original_url": "https://google.com"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    res = client.get(
        "/urls/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert res.status_code == 200

    data = res.json()

    assert len(data) == 1    


def test_delete_url(client):

    token = create_user_and_get_token(client)

    create_res = client.post(
        "/urls/shorten",
        json={
            "original_url": "https://google.com"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    url_id = create_res.json()["id"]

    res = client.delete(
        f"/urls/{url_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert res.status_code == 200  



def test_get_analytics(client):

    token = create_user_and_get_token(client)

    create_res = client.post(
        "/urls/shorten",
        json={
            "original_url": "https://google.com"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    url_id = create_res.json()["id"]

    res = client.get(
        f"/urls/{url_id}/analytics",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert res.status_code == 200

    data = res.json()

    assert data["id"] == url_id
    assert data["click_count"] == 0    



def test_unauthorized_analytics(client):

    user1_token = create_user_and_get_token(client)

    create_res = client.post(
        "/urls/shorten",
        json={
            "original_url": "https://google.com"
        },
        headers={
            "Authorization": f"Bearer {user1_token}"
        }
    )

    url_id = create_res.json()["id"]

    client.post(
        "/auth/register",
        json={
            "email": "user2@gmail.com",
            "password": "password123"
        }
    )

    login = client.post(
        "/auth/login",
        json={
            "email": "user2@gmail.com",
            "password": "password123"
        }
    )

    user2_token = login.json()["access_token"]

    res = client.get(
        f"/urls/{url_id}/analytics",
        headers={
            "Authorization": f"Bearer {user2_token}"
        }
    )

    assert res.status_code == 403      
