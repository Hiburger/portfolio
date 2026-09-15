import json
import os
import sys
import urllib.request

LOGIN = "Hiburger"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            contributionLevel
          }
        }
      }
    }
  }
}
"""

LEVELS = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}


def main():
    token = os.environ.get("CONTRIBS_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("no token available")
    body = json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": "Bearer " + token,
            "User-Agent": "portfolio-contribs-baker",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data or not data.get("data"):
        sys.exit("graphql error: " + json.dumps(data.get("errors", data)))
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [
        [
            {"c": d["contributionCount"], "l": LEVELS[d["contributionLevel"]]}
            for d in w["contributionDays"]
        ]
        for w in cal["weeks"]
    ]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    out = {
        "generated": days[-1]["date"],
        "total": cal["totalContributions"],
        "from": days[0]["date"],
        "to": days[-1]["date"],
        "weeks": weeks,
    }
    with open("contribs.json", "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print("baked", out["total"], "contributions", out["from"], "->", out["to"])


if __name__ == "__main__":
    main()
