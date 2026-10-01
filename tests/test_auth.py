VALID_USER_DATA = {
    "email": "alice@example.com",
    "username": "alice",
    "password": "very-strong-password",
}



def test_register_rejects_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "not-a-valid-email",
            "username": "alice",
            "password": "very-strong-password",
        },
    )

    response_data = response.json()

    assert response.status_code == 422
    assert "detail" in response_data
    assert response_data["detail"][0]["loc"] == ["body", "email"]


def test_register_user_successfully(client):
    response = client.post(
        "/auth/register",
        json=VALID_USER_DATA,
    )

    response_data = response.json()

    assert response.status_code == 201
    assert response_data["email"] == VALID_USER_DATA["email"]
    assert response_data["username"] == VALID_USER_DATA["username"]
    assert response_data["role"] == "user"
    assert "id" in response_data
    assert "password" not in response_data
    assert "hashed_password" not in response_data


def test_register_rejects_duplicate_email(client, registered_user):
    second_response = client.post(
        "/auth/register",
        json=registered_user,
    )

    assert second_response.status_code == 400
    assert second_response.json() == {
        "detail": "Email already registered",
    }


def test_register_rejects_duplicate_username(client, registered_user):
    second_user_data = {
        **registered_user,
        "email": "bob@example.com",
    }

    second_response = client.post(
        "/auth/register",
        json=second_user_data,
    )

    assert second_response.status_code == 400
    assert second_response.json() == {
        "detail": "Username already taken",
    }


def test_login_user_successfully(client, registered_user):
    login_response = client.post(
        "/auth/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    response_data = login_response.json()

    assert login_response.status_code == 200
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


def test_get_current_user_successfully(
    client,
    registered_user,
    auth_headers,
):

    me_response = client.get(
        "/auth/me",
        headers=auth_headers,
    )

    assert me_response.status_code == 200

    response_data = me_response.json()

    assert response_data["email"] == registered_user["email"]
    assert response_data["username"] == registered_user["username"]
    assert response_data["role"] == "user"
    assert "password" not in response_data
    assert "hashed_password" not in response_data


def test_get_current_user_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_get_current_user_rejects_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate credentials",
    }


def test_login_rejects_unknown_user(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "unknown@example.com",
            "password": "very-strong-password",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid credentials",
    }


def test_login_rejects_wrong_password(client, registered_user):
    response = client.post(
        "/auth/login",
        data={
            "username": registered_user["email"],
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid credentials",
    }
