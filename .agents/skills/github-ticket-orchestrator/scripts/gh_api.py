#!/usr/bin/env python3
"""Client léger sans dépendance externe pour l'API REST GitHub (Issues & Repos).

Utilisé par le skill `github-ticket-orchestrator`.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request

SCRATCH_ENV = Path(
    "/home/Yolpo/.gemini/antigravity/brain/53f9faee-2d05-411e-9e75-e00a975415ff/scratch/.env"
)
DEFAULT_BACKLOG_SPEC = (
    Path(__file__).resolve().parent.parent / "references" / "backlog_specs.json"
)


def load_token() -> str:
  if os.environ.get("GITHUB_TOKEN"):
    return os.environ["GITHUB_TOKEN"].strip()
  for env_path in [Path(".env"), SCRATCH_ENV, Path.home() / ".env"]:
    if env_path.is_file():
      for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("GITHUB_TOKEN="):
          return line.split("=", 1)[1].strip().strip("\"'")
  raise RuntimeError("GITHUB_TOKEN introuvable dans l'environnement ou .env")


def api_request(method: str, endpoint: str, payload: dict | None = None):
  token = load_token()
  url = (
      endpoint
      if endpoint.startswith("http")
      else f"https://api.github.com{endpoint}"
  )
  data = json.dumps(payload).encode("utf-8") if payload is not None else None
  req = urllib.request.Request(
      url,
      data=data,
      method=method,
      headers={
          "Authorization": f"Bearer {token}",
          "Accept": "application/vnd.github+json",
          "X-GitHub-Api-Version": "2022-11-28",
          "User-Agent": "Panique-A-Bord-Orchestrator",
          "Content-Type": "application/json",
      },
  )
  try:
    with urllib.request.urlopen(req, timeout=15) as resp:
      raw = resp.read().decode("utf-8")
      return json.loads(raw) if raw else {}
  except urllib.error.HTTPError as e:
    err_body = e.read().decode("utf-8", errors="replace")
    print(f"Erreur HTTP {e.code} sur {method} {url}: {err_body}", file=sys.stderr)
    sys.exit(1)


def normalize_repo(repo_val: str | list[str]) -> str:
  if isinstance(repo_val, list):
    repo_val = "/".join(repo_val)
  repo_val = repo_val.strip()
  if "/" in repo_val:
    owner, repo_name = repo_val.split("/", 1)
    if owner.lower() in ("yolpo", "yolepo"):
      owner = "Yolepo"
    return f"{owner}/{repo_name}"
  return f"Yolepo/{repo_val}"


def main():
  # Permet d'accepter indistinctement "owner/repo" ou "owner repo"
  new_argv = [sys.argv[0]]
  i = 1
  while i < len(sys.argv):
    arg = sys.argv[i]
    if i + 1 < len(sys.argv) and sys.argv[i].lower() in ("yolpo", "yolepo") and not sys.argv[i+1].startswith("-"):
      new_argv.append(f"{sys.argv[i]}/{sys.argv[i+1]}")
      i += 2
    else:
      new_argv.append(arg)
      i += 1
  sys.argv = new_argv

  parser = argparse.ArgumentParser(description="GitHub API Orchestrator CLI")
  sub = parser.add_subparsers(dest="cmd", required=True)

  sub.add_parser("whoami", help="Vérifie le compte GitHub connecté")

  p_repo = sub.add_parser("create-repo", help="Crée un dépôt GitHub")
  p_repo.add_argument("name", help="Nom du dépôt")
  p_repo.add_argument("--description", default="", help="Description du dépôt")
  p_repo.add_argument(
      "--private", action="store_true", help="Créer en dépôt privé"
  )

  p_del = sub.add_parser("delete-repo", help="Supprime un dépôt GitHub")
  p_del.add_argument("repo", nargs="+", help="Format owner/repo ou owner repo")

  p_init_bl = sub.add_parser(
      "init-backlog",
      help="Crée les 4 tickets GitHub détaillés depuis references/backlog_specs.json",
  )
  p_init_bl.add_argument("repo", nargs="+", help="Format owner/repo ou owner repo")
  p_init_bl.add_argument(
      "--spec",
      default=str(DEFAULT_BACKLOG_SPEC),
      help="Chemin du fichier JSON de spécifications du backlog",
  )

  p_list = sub.add_parser("list-issues", help="Liste les tickets GitHub")
  p_list.add_argument("repo", help="Format owner/repo")
  p_list.add_argument("--state", default="open", choices=["open", "closed", "all"])

  p_get = sub.add_parser("get-issue", help="Lit les détails complets d'un ticket")
  p_get.add_argument("repo", help="Format owner/repo")
  p_get.add_argument("number", type=int, help="Numéro du ticket")

  p_create = sub.add_parser("create-issue", help="Crée un ticket GitHub")
  p_create.add_argument("repo", help="Format owner/repo")
  p_create.add_argument("--title", required=True, help="Titre du ticket")
  p_create.add_argument("--body", required=True, help="Corps Markdown du ticket")
  p_create.add_argument(
      "--labels", default="", help="Labels séparés par des virgules"
  )

  p_comment = sub.add_parser("comment-issue", help="Ajoute un commentaire")
  p_comment.add_argument("repo", help="Format owner/repo")
  p_comment.add_argument("number", type=int, help="Numéro du ticket")
  p_comment.add_argument("--body", required=True, help="Commentaire Markdown")

  p_close = sub.add_parser("close-issue", help="Ferme un ticket GitHub")
  p_close.add_argument("repo", help="Format owner/repo")
  p_close.add_argument("number", type=int, help="Numéro du ticket")
  p_close.add_argument(
      "--comment", default="", help="Commentaire de clôture optionnel"
  )

  args = parser.parse_args()

  if args.cmd == "whoami":
    user = api_request("GET", "/user")
    print(
        json.dumps(
            {
                "login": user.get("login"),
                "name": user.get("name"),
                "html_url": user.get("html_url"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )

  elif args.cmd == "create-repo":
    res = api_request(
        "POST",
        "/user/repos",
        {
            "name": args.name,
            "description": args.description,
            "private": args.private,
            "has_issues": True,
            "auto_init": False,
        },
    )
    print(
        json.dumps(
            {
                "full_name": res.get("full_name"),
                "html_url": res.get("html_url"),
                "clone_url": res.get("clone_url"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )

  elif args.cmd == "delete-repo":
    repo = normalize_repo(args.repo)
    api_request("DELETE", f"/repos/{repo}")
    print(json.dumps({"deleted": repo}, indent=2, ensure_ascii=False))

  elif args.cmd == "init-backlog":
    repo = normalize_repo(args.repo)
    spec_path = Path(args.spec)
    specs = json.loads(spec_path.read_text(encoding="utf-8"))
    created = []
    for item in specs:
      payload = {
          "title": item["title"],
          "body": item["body"],
          "labels": item.get("labels", []),
      }
      res = api_request("POST", f"/repos/{repo}/issues", payload)
      created.append(
          {
              "number": res["number"],
              "title": res["title"],
              "html_url": res["html_url"],
          }
      )
    print(json.dumps(created, indent=2, ensure_ascii=False))

  elif args.cmd == "list-issues":
    repo = normalize_repo(args.repo)
    issues = api_request(
        "GET", f"/repos/{repo}/issues?state={args.state}&per_page=50"
    )
    out = [
        {
            "number": i["number"],
            "title": i["title"],
            "state": i["state"],
            "labels": [lbl["name"] for lbl in i.get("labels", [])],
            "html_url": i["html_url"],
        }
        for i in issues
        if "pull_request" not in i
    ]
    print(json.dumps(out, indent=2, ensure_ascii=False))

  elif args.cmd == "get-issue":
    repo = normalize_repo(args.repo)
    issue = api_request("GET", f"/repos/{repo}/issues/{args.number}")
    comments = api_request(
        "GET", f"/repos/{repo}/issues/{args.number}/comments"
    )
    print(
        json.dumps(
            {
                "number": issue["number"],
                "title": issue["title"],
                "state": issue["state"],
                "labels": [lbl["name"] for lbl in issue.get("labels", [])],
                "body": issue.get("body", ""),
                "comments": [
                    {
                        "user": c["user"]["login"],
                        "created_at": c["created_at"],
                        "body": c["body"],
                    }
                    for c in comments
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
    )

  elif args.cmd == "create-issue":
    repo = normalize_repo(args.repo)
    labels = [l.strip() for l in args.labels.split(",") if l.strip()]
    payload = {"title": args.title, "body": args.body}
    if labels:
      payload["labels"] = labels
    res = api_request("POST", f"/repos/{repo}/issues", payload)
    print(
        json.dumps(
            {
                "number": res["number"],
                "title": res["title"],
                "html_url": res["html_url"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )

  elif args.cmd == "comment-issue":
    repo = normalize_repo(args.repo)
    res = api_request(
        "POST",
        f"/repos/{repo}/issues/{args.number}/comments",
        {"body": args.body},
    )
    print(
        json.dumps(
            {"id": res["id"], "html_url": res["html_url"]},
            indent=2,
            ensure_ascii=False,
        )
    )

  elif args.cmd == "close-issue":
    repo = normalize_repo(args.repo)
    if args.comment:
      api_request(
          "POST",
          f"/repos/{repo}/issues/{args.number}/comments",
          {"body": args.comment},
      )
    res = api_request(
        "PATCH",
        f"/repos/{repo}/issues/{args.number}",
        {"state": "closed"},
    )
    print(
        json.dumps(
            {
                "number": res["number"],
                "state": res["state"],
                "html_url": res["html_url"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
  main()
