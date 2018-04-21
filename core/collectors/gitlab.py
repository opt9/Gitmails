from core.models.user import User
from core.models.author import Author
from core.utils.helpers import Helpers
from core.models.collector import Collector
from core.models.repository import Repository
from core.models.organization import Organization

class GitlabCollector(Collector):
    def __init__(self, args):
        self.args = args
        self.base_url = "https://gitlab.com/api/v4"

    def collect_user(self, username):
        userid = self.get_userid(username)
        url = "{}/users/{}".format(self.base_url, userid)
        result = Helpers().request(url)
        if result:
            repos = self.collect_repositories("{}/users/{}/projects".format(self.base_url, userid))
            return User(result["username"], result["name"], None, result["bio"], repos)
        return False

    def collect_organization(self, organization):
        url = "{}/groups/{}".format(self.base_url, organization)
        result = Helpers().request(url)
        if result:
            repos = self.parse_repositories(result["projects"])
            self.get_collaborators(repos)
            return Organization(result["full_name"], None, None, repos, None)
        return False

    def collect_repositories(self, repos_url):
        result = Helpers().request(repos_url)
        repos = self.parse_repositories(result) if result else []
        self.get_collaborators(repos)
        return repos

    def parse_repositories(self, request_result):
        return [Repository(repo["id"], repo["name"], repo["http_url_to_repo"], None) for repo in request_result if request_result]

    def get_collaborators(self, repos):
        if repos:
            for repo in repos:
                repo.set_authors(self.repository_collaborators(repo.identifier))
            return True
        return False

    def repository_collaborators(self, repoid):
        url = "{}/projects/{}/repository/contributors".format(self.base_url, repoid)
        result = Helpers().request(url)
        return [Author(contributor["name"], contributor["email"]) for contributor in result if result]

    def get_userid(self, username):
        url = "{}/users?username={}".format(self.base_url, username)
        result = Helpers().request(url)
        if result:
            return result[0]["id"]
        return False

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
