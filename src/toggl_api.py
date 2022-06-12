import json
import base64
import urllib.request

class Toggl():
    def __init__(self, api_key):
        self._API_KEY = api_key

    def get_projects(self, workspace_id):
        URL = f"https://api.track.toggl.com/api/v8/workspaces/{workspace_id}/projects"

        auth_string = f"{self._API_KEY}:api_token"
        auth_string = base64.standard_b64encode(auth_string.encode('utf-8'))

        headers = {
            "Authorization": f"Basic {auth_string.decode('utf-8')}"
        }

        req = urllib.request.Request(
            URL, headers=headers
        )

        res = ""
        with urllib.request.urlopen(req) as f:
            res = f.read().decode("utf-8")

        response = json.loads(res)
        projects = self.parse_projects(response)

        return projects

    def parse_projects(self, projects_response):
        projects = []
        for project in projects_response:
            project_obj = {
                "id": project["id"],
                "name": project["name"],
                "client_id": project["cid"] if "cid" in project else None
            }

            projects.append(project_obj)

        return projects
