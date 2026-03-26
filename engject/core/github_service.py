import requests

# ==============================
# COMMON HEADERS (Avoid rate limits)
# ==============================
HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "EngJect-It-App"
}


# ==============================
# GET SINGLE REPO DETAILS
# ==============================
def get_repo_details(owner, repo_name):
    try:
        base_url = f"https://api.github.com/repos/{owner}/{repo_name}"

        repo_res = requests.get(base_url, headers=HEADERS, timeout=5)
        readme_res = requests.get(
            f"{base_url}/readme",
            headers={
                "Accept": "application/vnd.github.v3.raw",
                "User-Agent": "EngJect-It-App"
            },
            timeout=5
        )

        if repo_res.status_code != 200:
            return None

        repo = repo_res.json()

        # Clean README (limit size)
        if readme_res.status_code == 200:
            readme = readme_res.text[:1500]  # limit for UI
        else:
            readme = "No README available."

        return {
            "name": repo.get("name"),
            "description": repo.get("description"),
            "stars": repo.get("stargazers_count"),
            "forks": repo.get("forks_count"),
            "language": repo.get("language"),
            "owner": repo.get("owner", {}).get("login"),
            "avatar": repo.get("owner", {}).get("avatar_url"),
            "readme": readme,
            "url": repo.get("html_url"),
            "created_at": repo.get("created_at"),
            "topics": repo.get("topics", [])
        }

    except Exception as e:
        print("Error fetching repo details:", e)
        return None


# ==============================
# SEARCH REPOSITORIES
# ==============================
def fetch_github_repos(query):
    try:
        url = "https://api.github.com/search/repositories"

        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 6
        }

        response = requests.get(url, headers=HEADERS, params=params, timeout=5)

        if response.status_code != 200:
            return []

        data = response.json()
        repos = []

        for item in data.get("items", []):

            repos.append({
                "name": item.get("name"),
                "full_name": item.get("full_name"),
                "description": item.get("description"),
                "stars": item.get("stargazers_count"),
                "url": item.get("html_url"),
                "owner": item.get("owner", {}).get("login"),
                "avatar": item.get("owner", {}).get("avatar_url"),
                "language": item.get("language"),
                "created_at": item.get("created_at")
            })

        return repos

    except Exception as e:
        print("Error fetching repos:", e)
        return []