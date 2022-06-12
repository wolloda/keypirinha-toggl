import json
import base64
import urllib.request, urllib.error

class Toggler():
    def __init__(self, api_token):
        self._API_TOKEN = api_token

    def get_projects(self, workspace_id):
        URL = f"https://api.track.toggl.com/api/v8/workspaces/{workspace_id}/projects"

        response = self._make_request(URL)
        try:
            projects = self.parse_projects(response)
        except urllib.error.HTTPError:
            projects = None

        return projects

    def parse_projects(self, projects_response):
        projects = []
        for project in projects_response:
            client_id = project["cid"] if "cid" in project else None
            client = None

            if client_id:
                client = self.get_client(client_id)

            project_obj = {
                "id": str(project["id"]),
                "name": project["name"],
                "client": client
            }

            projects.append(project_obj)

        return projects

    def get_client(self, client_id: str):
        if not client_id:
            return None

        URL = f"https://api.track.toggl.com/api/v8/clients/{client_id}"

        try:
            response = self._make_request(URL)
            response = response["data"]["name"]
        except urllib.error.HTTPError:
            response = None

        return response

    def start_timer(self, description: str, project_id: str):
        URL = "https://api.track.toggl.com/api/v8/time_entries/start"

        data = {
            "time_entry": {
                "description": description,
                "pid": int(project_id),
                "created_with": "Keypirinha"
            }
        }

        _ = self._make_request(URL, data)

    def stop_timer(self):
        running_time_entry = self.get_running_time_entry()
        if not running_time_entry or not running_time_entry["data"]:
            return

        time_entry_id = running_time_entry["data"]["id"]
        URL = f"https://api.track.toggl.com/api/v8/time_entries/{time_entry_id}/stop"

        self._make_request(URL)




    def get_running_time_entry(self):
        URL = "https://api.track.toggl.com/api/v8/time_entries/current"

        try:
            response = self._make_request(URL)
        except:
            response = None

        return response


    def _make_request(self, URL: str, data = None):
        auth_string = f"{self._API_TOKEN}:api_token"
        auth_string = base64.standard_b64encode(auth_string.encode('utf-8'))

        headers = {
            "Authorization": f"Basic {auth_string.decode('utf-8')}",
            "Content-Type": "application/json"
        }

        if data:
            print(json.dumps(data))
            print(json.dumps(data).encode())

            req = urllib.request.Request(
                URL, json.dumps(data).encode(), headers=headers
            )
        else:
            req = urllib.request.Request(
                URL, headers=headers
            )

        res = ""
        with urllib.request.urlopen(req) as f:
            res = f.read().decode("utf-8")

        response = json.loads(res)

        return response
