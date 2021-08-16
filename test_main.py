from fastapi.testclient import TestClient

import config
from main import app
from models.authenticate import RequestAuthenticateModel
from fastapi.encoders import jsonable_encoder
from helpers.log import Log

client = TestClient(app)

glo_access_token = None
glo_work_id = None
glo_employer_id = None
glo_event_id = None
glo_report_id = None


def __create_work(work_name, hour_loan, access_token) -> str:
    response = client.post('/work/', json={"name": work_name, "hour_loan": hour_loan},
                           headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    json = response.json()
    assert "name" in json and json["name"] == work_name
    assert "hour_loan" in json and json["hour_loan"] == hour_loan
    return json["_id"]


def __create_employer(employer_name, employer_email, access_token) -> str:
    response = client.post("/employer/", json={"name": employer_name, "email": employer_email},
                           headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    json = response.json()

    assert "name" in json and json["name"] == employer_name
    assert "email" in json and json["email"] == employer_email
    assert "_id" in json
    return json["_id"]


def __create_event(work_id, from_time, to_time, based_on_hour_loan, loan_on_top, name, description, access_token):
    global glo_access_token
    response = client.post("/event/", json={"work": work_id, "from_time": from_time, "to_time": to_time,
                                            "based_on_hour_loan": based_on_hour_loan, "loan_on_top": loan_on_top,
                                            "name": name, "description": description},
                           headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    json = response.json()
    assert "work" in json and json["work"] == work_id
    assert "from_time" in json and json["from_time"] == from_time
    assert "to_time" in json and json["to_time"] == to_time
    assert "based_on_hour_loan" in json and json["based_on_hour_loan"] == based_on_hour_loan
    assert "loan_on_top" in json and json["loan_on_top"] == loan_on_top
    assert "name" in json and json["name"] == name
    assert "description" in json and json["description"] == description

    assert "_id" in json
    return json["_id"]


def __create_report(work_id, events_ids, access_token):
    response = client.post("/report/", json={"work_id": work_id, "events_ids": events_ids},
                           headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    json = response.json()

    assert "work" in json and "_id" in json["work"] and json["work"]["_id"] == work_id
    assert "events" in json and len(json["events"]) == len(events_ids)
    assert "_id" in json["events"][0] and json["events"][0]["_id"] == events_ids[0]
    assert "employers" in json and len(json["employers"]) == 1

    global glo_employer_id
    assert "_id" in json["employers"][0] and json["employers"][0]["_id"] == glo_employer_id

    assert "_id" in json
    return json["_id"]


def test_wipe_all():
    response = client.get(f"/wipe/{config.SECRET_KEY}")
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_auth():
    response = client.post('/auth/', data={"username": "kacper", "password": "kacper"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    global glo_access_token
    glo_access_token = response.json()['access_token']


def test_auth_invalid():
    response = client.post('/auth/', data={"username": "invalid", "password": "invalidtoo"})
    assert response.status_code == 401


def test_auth_me():
    global glo_access_token
    response = client.get("/auth/me", headers={"Authorization": f'Bearer {glo_access_token}'})
    assert response.status_code == 200
    assert response.json()['username'] == 'kacper'


def test_work_create():
    work_name = "Test Work"
    hour_loan = 10.00

    global glo_access_token, glo_work_id
    glo_work_id = __create_work(work_name, hour_loan, glo_access_token)


def test_work_update():
    updated_name = "New test work"
    global glo_access_token, glo_work_id
    response = client.put(f'/work/{glo_work_id}', json={"name": updated_name},
                          headers={"Authorization": f'Bearer {glo_access_token}'})
    assert response.status_code == 200
    json = response.json()
    assert "name" in json and json["name"] == updated_name


def test_work_specific():
    global glo_access_token, glo_work_id
    response = client.get(f"/work/{glo_work_id}", headers={"Authorization": f"Bearer {glo_access_token}"})
    assert response.status_code == 200
    json = response.json()
    assert "name" in json
    assert "hour_loan" in json
    assert "_id" in json and json["_id"] == glo_work_id


def test_work_second_work_in_list():
    second_work_name = "Second work name"
    second_hour_loan = 0.0
    global glo_access_token
    new_work_id = __create_work(second_work_name, second_hour_loan, glo_access_token)

    response = client.get("/work", headers={'Authorization': f'Bearer {glo_access_token}'})
    assert response.status_code == 200
    assert len(response.json()) >= 2

    found_first = False
    found_second = False

    for work in response.json():
        assert "_id" in work
        if work["_id"] == new_work_id:
            found_second = True
        global glo_work_id
        if work["_id"] == glo_work_id:
            found_first = True

    assert found_first
    assert found_second


def test_employer_create():
    employer_name = "My Employer"
    employer_email = "employer@3rd.party"
    global glo_access_token, glo_employer_id
    glo_employer_id = __create_employer(employer_name, employer_email, glo_access_token)


def test_employer_update():
    employer_address = "ABC 2, 234, The Netherlands"
    global glo_access_token, glo_employer_id
    response = client.put(f"/employer/{glo_employer_id}", json={"address": employer_address},
                          headers={"Authorization": f"Bearer {glo_access_token}"})

    assert response.status_code == 200
    json = response.json()
    assert "address" in json and json["address"] == employer_address


def test_employer_specific():
    global glo_access_token, glo_employer_id
    response = client.get(f'/employer/{glo_employer_id}', headers={'Authorization': f'Bearer {glo_access_token}'})
    assert response.status_code == 200
    json = response.json()
    assert "_id" in json and json["_id"] == glo_employer_id


def test_employer_second_e_in_the_list():
    second_employer_name = "Second employer"
    second_employer_email = "SecondEmail@fsd.com"
    global glo_access_token
    new_employer_id = __create_employer(second_employer_name, second_employer_email, glo_access_token)
    response = client.get("/employer", headers={'Authorization': f'Bearer {glo_access_token}'})
    assert response.status_code == 200
    assert len(response.json()) >= 2

    found_first = False
    found_second = False

    for employer in response.json():
        assert "_id" in employer
        if employer["_id"] == new_employer_id:
            found_second = True
        global glo_employer_id
        if employer["_id"] == glo_employer_id:
            found_first = True

    assert found_first
    assert found_second


# tsgfdsfd

def test_event_create():
    global glo_access_token, glo_work_id, glo_event_id
    glo_event_id = __create_event(glo_work_id, 0, 60, True, 10, "Test name", "Test description", glo_access_token)


def test_event_update():
    event_new_name = "Updated event"
    global glo_access_token, glo_event_id
    response = client.put(f"/event/{glo_event_id}", json={"name": event_new_name},
                          headers={"Authorization": f"Bearer {glo_access_token}"})
    assert response.status_code == 200
    json = response.json()
    assert "name" in json and json["name"] == event_new_name


def test_event_specific():
    global glo_access_token, glo_event_id
    response = client.get(f'/event/{glo_event_id}', headers={'Authorization': f'Bearer {glo_access_token}'})
    assert response.status_code == 200
    json = response.json()
    assert "_id" in json and json["_id"] == glo_event_id


def test_event_second_e_in_the_list():
    global glo_access_token, glo_work_id
    new_event_id = __create_event(glo_work_id, 120, 180, False, 60, "Second event", "Desc!", glo_access_token)
    response = client.get("/event", headers={'Authorization': f'Bearer {glo_access_token}'})
    assert response.status_code == 200
    assert len(response.json()) >= 2

    found_first = False
    found_second = False

    for event in response.json():
        assert "_id" in event
        if event["_id"] == new_event_id:
            found_second = True
        global glo_event_id
        if event["_id"] == glo_event_id:
            found_first = True

    assert found_first
    assert found_second


def test_add_employer_to_work():
    global glo_access_token, glo_work_id, glo_employer_id
    response = client.put(f'/work/{glo_work_id}', json={"employers": [glo_employer_id]},
                          headers={"Authorization": f'Bearer {glo_access_token}'})
    assert response.status_code == 200
    json = response.json()
    assert "employers" in json and len(json["employers"]) == 1
    assert glo_employer_id in json["employers"] and json["employers"][0] == glo_employer_id


def test_report_create():
    global glo_access_token, glo_work_id, glo_event_id, glo_report_id
    glo_report_id = __create_report(glo_work_id, [glo_event_id], glo_access_token)


def test_report_specific():
    global glo_access_token, glo_report_id
    response = client.get(f'/report/{glo_report_id}', headers={'Authorization': f'Bearer {glo_access_token}'})
    assert response.status_code == 200
    json = response.json()
    assert "_id" in json and json["_id"] == glo_report_id


def test_report_second_e_in_the_list():
    global glo_access_token, glo_work_id
    new_report_id = __create_report(glo_work_id, [glo_event_id], glo_access_token)
    response = client.get("/report", headers={'Authorization': f'Bearer {glo_access_token}'})
    assert response.status_code == 200
    assert len(response.json()) >= 2

    found_first = False
    found_second = False

    for report in response.json():
        assert "_id" in report
        if report["_id"] == new_report_id:
            found_second = True
        global glo_report_id
        if report["_id"] == glo_report_id:
            found_first = True

    assert found_first
    assert found_second
