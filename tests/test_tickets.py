VALID_TICKET_DATA = {
    "title": "Wi-Fi is not working",
    "description": "The office Wi-Fi router is on fire",
}


def test_create_ticket_successfully(client, auth_headers):
    response = client.post(
        "/tickets/",
        json=VALID_TICKET_DATA,
        headers=auth_headers,
    )

    response_data = response.json()

    assert response.status_code == 201
    assert response_data["title"] == VALID_TICKET_DATA["title"]
    assert response_data["description"] == VALID_TICKET_DATA["description"]
    assert response_data["status"] == "open"
    assert "id" in response_data
    assert "owner_id" in response_data
    assert "created_at" in response_data


def test_create_ticket_requires_authentication(client):
    response = client.post(
        "/tickets/",
        json=VALID_TICKET_DATA,
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not authenticated",
    }


def test_create_ticket_rejects_short_title(client, auth_headers):
    invalid_ticket_data = {
        **VALID_TICKET_DATA,
        "title": "ab",
    }

    response = client.post(
        "/tickets/",
        json=invalid_ticket_data,
        headers=auth_headers,
    )

    response_data = response.json()

    assert response.status_code == 422
    assert "detail" in response_data
    assert response_data["detail"][0]["loc"] == ["body", "title"]


def test_get_my_tickets_returns_created_tickets(client, auth_headers):
    second_ticket_data = {
        **VALID_TICKET_DATA,
        "title": "VPN connection is unavailable",
    }

    first_response = client.post(
        "/tickets/",
        json=VALID_TICKET_DATA,
        headers=auth_headers,
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/tickets/",
        json=second_ticket_data,
        headers=auth_headers,
    )
    assert second_response.status_code == 201

    list_response = client.get(
        "/tickets/",
        headers=auth_headers,
    )

    assert list_response.status_code == 200

    response_data = list_response.json()

    assert isinstance(response_data, list)
    assert len(response_data) == 2

    returned_titles = {
        ticket["title"]
        for ticket in response_data
    }

    assert returned_titles == {
        VALID_TICKET_DATA["title"],
        second_ticket_data["title"],
    }


def test_get_my_tickets_returns_empty_list(client, auth_headers):
    response = client.get(
        "/tickets/",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_my_tickets_excludes_other_users_tickets(
    client,
    auth_headers,
    second_auth_headers,
):
    create_response = client.post(
        "/tickets/",
        json=VALID_TICKET_DATA,
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    list_response = client.get(
        "/tickets/",
        headers=second_auth_headers,
    )

    assert list_response.status_code == 200
    assert list_response.json() == []


def test_get_my_ticket_successfully(client, auth_headers):
    create_response = client.post(
        "/tickets/",
        json=VALID_TICKET_DATA,
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    created_ticket = create_response.json()
    ticket_id = created_ticket["id"]

    get_response = client.get(
        f"/tickets/{ticket_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200

    response_data = get_response.json()

    assert response_data["id"] == ticket_id
    assert response_data["title"] == VALID_TICKET_DATA["title"]
    assert response_data["description"] == VALID_TICKET_DATA["description"]
    assert response_data["status"] == "open"
    assert response_data["owner_id"] == created_ticket["owner_id"]
    assert response_data["created_at"] == created_ticket["created_at"]


def test_get_my_ticket_returns_404_for_unknown_ticket(
    client,
    auth_headers,
):
    create_response = client.get(
        "/tickets/999999",
        headers=auth_headers,
    )

    assert create_response.status_code == 404
    assert create_response.json() == {
        "detail": "Ticket not found",
    }


def test_get_my_ticket_returns_404_for_other_users_ticket(
    client,
    auth_headers,
    second_auth_headers,
):
    create_response = client.post(
        "/tickets/",
        json=VALID_TICKET_DATA,
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    ticket_id = create_response.json()["id"]

    get_response = client.get(
        f"/tickets/{ticket_id}",
        headers=second_auth_headers,
    )

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Ticket not found",
    }


def test_get_my_ticket_requires_authentication(client):
    response = client.get("/tickets/1")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not authenticated",
    }


def test_update_ticket_status_rejects_regular_user(
    client,
    auth_headers,
):
    create_response = client.post(
        "/tickets/",
        json=VALID_TICKET_DATA,
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    ticket_id = create_response.json()["id"]

    update_response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "status": "resolved",
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 403
    assert update_response.json() == {
        "detail": "Not enough permissions",
    }


def test_update_ticket_status_successfully(
    client,
    auth_headers,
    support_auth_headers,
):
    create_response = client.post(
        "/tickets/",
        json=VALID_TICKET_DATA,
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    created_ticket = create_response.json()
    ticket_id = created_ticket["id"]

    update_response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "status": "in_progress",
        },
        headers=support_auth_headers,
    )

    assert update_response.status_code == 200

    response_data = update_response.json()

    assert response_data["id"] == ticket_id
    assert response_data["status"] == "in_progress"
    assert response_data["owner_id"] == created_ticket["owner_id"]
    assert response_data["title"] == VALID_TICKET_DATA["title"]


def test_update_ticket_status_returns_404_for_unknown_ticket(
    client,
    support_auth_headers,
):
    response = client.patch(
        "/tickets/999999/status",
        json={
            "status": "resolved",
        },
        headers=support_auth_headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Ticket not found",
    }


def test_update_ticket_status_rejects_invalid_status(
    client,
    auth_headers,
    support_auth_headers,
):
    create_response = client.post(
        "/tickets/",
        json=VALID_TICKET_DATA,
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    ticket_id = create_response.json()["id"]

    update_response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "status": "reopened",
        },
        headers=support_auth_headers,
    )

    assert update_response.status_code == 422

    response_data = update_response.json()

    assert "detail" in response_data
    assert response_data["detail"][0]["loc"] == ["body", "status"]


def test_update_ticket_status_requires_authentication(client):
    response = client.patch(
        "/tickets/1/status",
        json={
            "status": "resolved",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not authenticated",
    }
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_update_ticket_status_successfully_by_admin(
    client,
    auth_headers,
    admin_auth_headers,
):
    create_response = client.post(
        "/tickets/",
        json=VALID_TICKET_DATA,
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    ticket_id = create_response.json()["id"]

    update_response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "status": "closed",
        },
        headers=admin_auth_headers,
    )

    assert update_response.status_code == 200

    response_data = update_response.json()

    assert response_data["id"] == ticket_id
    assert response_data["status"] == "closed"