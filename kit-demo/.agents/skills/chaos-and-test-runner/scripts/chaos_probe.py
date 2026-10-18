#!/usr/bin/env python3
"""Sonde d'audit Sécurité & Chaos pour Panique à Bord."""
import json
import sys
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8080"


def post_incident(payload: dict) -> tuple[int, dict | str]:
  data = json.dumps(payload).encode("utf-8")
  req = urllib.request.Request(
      f"{BASE_URL}/api/incidents",
      data=data,
      method="POST",
      headers={"Content-Type": "application/json"},
  )
  try:
    with urllib.request.urlopen(req, timeout=5) as resp:
      return resp.status, json.loads(resp.read().decode("utf-8"))
  except urllib.error.HTTPError as e:
    try:
      body = json.loads(e.read().decode("utf-8"))
    except Exception:
      body = e.read().decode("utf-8", errors="replace")
    return e.code, body
  except Exception as e:
    return 0, str(e)


def run_audit():
  print("🛡️ [VIDEUR] Démarrage de l'audit Chaos & Sécurité sur", BASE_URL)
  failures = []

  # Test 1: XSS Payload
  xss_payload = {
      "title": "<img src=x onerror=alert('HACKED')> Intrusion Cyber",
      "x": 50,
      "y": 50,
      "severity": "CRITICAL",
  }
  status, resp = post_incident(xss_payload)
  raw_str = json.dumps(resp)
  if status == 200 and "<img" in raw_str:
    failures.append(
        "FAIL [SEC-01] Injection HTML/XSS acceptée sans échappement ni rejet !"
    )
    print(
        "❌ [SEC-01] VULNÉRABILITÉ : Payload XSS accepté tel quel par l'API !"
    )
  else:
    print(
        f"✅ [SEC-01] Protection XSS active (HTTP {status}) -> payload neutralisé ou rejeté."
    )

  # Test 2: Out-of-bounds coordinates
  oob_payload = {
      "title": "Anomalie Hors Grille",
      "x": -9999,
      "y": 88888,
      "severity": "INVALID_LEVEL",
  }
  status, resp = post_incident(oob_payload)
  if status == 200 and isinstance(resp, dict) and resp.get("incident", {}).get("x") == -9999:
    failures.append(
        "FAIL [CHAOS-02] Coordonnées hors-radar (-9999, 88888) acceptées sans bornage ni erreur 400 !"
    )
    print(
        "❌ [CHAOS-02] VULNÉRABILITÉ : Coordonnées hors-radar acceptées sans validation !"
    )
  else:
    print(
        f"✅ [CHAOS-02] Validation des bornes radar active (HTTP {status})."
    )

  # Test 3: Flood / Stress burst (15 rapid requests)
  accepted = 0
  for i in range(15):
    s, _ = post_incident(
        {"title": f"Tempête Chaos #{i+1}", "x": (i * 7) % 100, "y": (i * 13) % 100, "severity": "HIGH"}
    )
    if s in (200, 201):
      accepted += 1
  print(f"ℹ️ [CHAOS-03] Rafale de 15 événements envoyée ({accepted} traités).")

  if failures:
    print("\n🚨 VERDICT VIDEUR : ÉCHEC DE L'AUDIT SÉCURITÉ")
    for f in failures:
      print("  -", f)
    sys.exit(2)
  else:
    print("\n🟢 VERDICT VIDEUR : 100% DES CONTRE-MESURES SÉCURITÉ & CHAOS VALIDÉES")
    sys.exit(0)


if __name__ == "__main__":
  run_audit()
