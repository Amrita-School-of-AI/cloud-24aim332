#!/usr/bin/env python3
"""
Checker for icc-ex02. Run one stage at a time so agrade can award marks per
stage and the student sees which requirement failed.

    check.py manifest.yaml --stage parse|deployment|service|production

Exit code 0 means the stage passed. Every failure prints one line beginning
"FAIL: " so the feedback PDF is readable without the grader's help.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

FAILS: list[str] = []


def fail(msg: str) -> None:
    FAILS.append(msg)
    print(f"FAIL: {msg}")


def ok(msg: str) -> None:
    print(f"  ok  {msg}")


def load(path: Path) -> list[dict]:
    try:
        docs = [d for d in yaml.safe_load_all(path.read_text(encoding="utf-8")) if d]
    except yaml.YAMLError as e:
        fail(f"the file is not valid YAML: {e}")
        return []
    return docs


def find(docs: list[dict], kind: str) -> dict | None:
    for d in docs:
        if isinstance(d, dict) and d.get("kind") == kind:
            return d
    return None


def dig(d, *keys, default=None):
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k)
        if d is None:
            return default
    return d


# ---------------------------------------------------------------------------

def stage_parse(docs: list[dict], path: Path) -> None:
    if not docs:
        fail("no YAML documents found")
        return
    ok(f"{len(docs)} YAML document(s) parsed")

    for d in docs:
        if not d.get("apiVersion") or not d.get("kind"):
            fail(f"a document is missing apiVersion or kind: {str(d)[:70]}")
    if not FAILS:
        ok("every document has apiVersion and kind")

    # Validate with kubectl when it is available. Full schema validation needs a
    # reachable cluster, because kubectl downloads the OpenAPI document from the
    # API server. On a laptop with no cluster that is not a student error, so
    # fall back to structural validation rather than failing them for it.
    if not shutil.which("kubectl"):
        print("  note: kubectl not available, structural checks only")
        return

    # Even `--dry-run=client --validate=false` contacts the API server, because
    # kubectl has to map a kind to a resource through the discovery endpoint.
    # With no cluster that is an environment limitation, not a student error, so
    # probe first and skip rather than failing them for it. In the lab, where a
    # kind or minikube cluster is running, this path does execute.
    probe = subprocess.run(["kubectl", "api-versions", "--request-timeout=3s"],
                           capture_output=True, text=True)
    if probe.returncode != 0:
        print("  note: no reachable cluster, so kubectl validation was skipped. "
              "Run this again with `kind create cluster` up to get full schema "
              "validation.")
        return

    r = subprocess.run(
        ["kubectl", "apply", "--dry-run=client", "--validate=true", "-f", str(path)],
        capture_output=True, text=True)
    if r.returncode != 0:
        fail("kubectl rejected the manifest:\n" + (r.stderr or r.stdout)[-800:])
    else:
        ok("kubectl accepted the manifest (schema validated against the cluster)")


def stage_deployment(docs: list[dict]) -> None:
    dep = find(docs, "Deployment")
    if not dep:
        fail("no Deployment found")
        return
    ok("Deployment present")

    if dep.get("apiVersion") != "apps/v1":
        fail(f"Deployment apiVersion should be apps/v1, found {dep.get('apiVersion')!r}")

    reps = dig(dep, "spec", "replicas")
    if reps != 3:
        fail(f"expected 3 replicas, found {reps!r}")
    else:
        ok("3 replicas")

    sel = dig(dep, "spec", "selector", "matchLabels", default={}) or {}
    lbl = dig(dep, "spec", "template", "metadata", "labels", default={}) or {}
    if not sel:
        fail("spec.selector.matchLabels is missing")
    elif not all(lbl.get(k) == v for k, v in sel.items()):
        fail(f"the selector {sel} does not match the pod template labels {lbl}; "
             "the Deployment would manage no pods")
    else:
        ok("selector matches the pod template labels")

    conts = dig(dep, "spec", "template", "spec", "containers", default=[]) or []
    if len(conts) != 1:
        fail(f"expected exactly one container, found {len(conts)}")
        return
    c = conts[0]

    img = c.get("image", "")
    if img != "ghcr.io/example/web:1.4.2":
        if img.endswith(":latest") or ":" not in img:
            fail("the image must carry a real version tag; `latest` (or no tag) "
                 "makes rollbacks impossible and lets two nodes run different code")
        else:
            fail(f"expected image ghcr.io/example/web:1.4.2, found {img!r}")
    else:
        ok("image pinned to a real version")

    ports = c.get("ports", []) or []
    if not any(p.get("containerPort") == 8080 for p in ports):
        fail("containerPort 8080 is not declared")
    else:
        ok("containerPort 8080")


def stage_service(docs: list[dict]) -> None:
    svc = find(docs, "Service")
    dep = find(docs, "Deployment")
    if not svc:
        fail("no Service found")
        return
    ok("Service present")

    sel = dig(svc, "spec", "selector", default={}) or {}
    lbl = dig(dep, "spec", "template", "metadata", "labels", default={}) or {}
    if not sel:
        fail("the Service has no selector, so it would route to nothing")
    elif not all(lbl.get(k) == v for k, v in sel.items()):
        fail(f"the Service selector {sel} does not match the pod labels {lbl}; "
             "the Service would have no endpoints")
    else:
        ok("Service selector matches the Deployment's pods")

    ports = dig(svc, "spec", "ports", default=[]) or []
    good = any(p.get("port") == 80 and p.get("targetPort") in (8080, "8080")
               for p in ports)
    if not good:
        fail(f"expected port 80 forwarding to targetPort 8080, found {ports}")
    else:
        ok("port 80 -> targetPort 8080")


SECRET_RE = re.compile(
    r"(?i)\b(password|passwd|secret|token|api[_-]?key|access[_-]?key)\b\s*:\s*"
    r"(?!\s*$)(?!.*valueFrom)(?!.*secretKeyRef)\S+")


def stage_production(docs: list[dict], path: Path) -> None:
    dep = find(docs, "Deployment")
    if not dep:
        fail("no Deployment found")
        return
    conts = dig(dep, "spec", "template", "spec", "containers", default=[]) or []
    if not conts:
        fail("no container found")
        return
    c = conts[0]

    # --- probes ---
    live, ready = c.get("livenessProbe"), c.get("readinessProbe")
    if not live:
        fail("no livenessProbe")
    if not ready:
        fail("no readinessProbe")
    if live and ready:
        lp = dig(live, "httpGet", "path")
        rp = dig(ready, "httpGet", "path")
        if not lp or not rp:
            fail("both probes must be httpGet with a path")
        elif lp == rp:
            fail(f"both probes use the same path {lp!r}. They answer different "
                 "questions: liveness failing RESTARTS the container, readiness "
                 "failing only removes it from the Service. A liveness probe that "
                 "checks dependencies restarts every pod during a dependency blip")
        else:
            ok(f"distinct probe paths: liveness {lp}, readiness {rp}")

    # --- resources ---
    req = dig(c, "resources", "requests", default={}) or {}
    lim = dig(c, "resources", "limits", default={}) or {}
    missing = [f"requests.{k}" for k in ("cpu", "memory") if k not in req]
    missing += [f"limits.{k}" for k in ("cpu", "memory") if k not in lim]
    if missing:
        fail("missing " + ", ".join(missing) +
             ". Requests drive scheduling and horizontal autoscaling; without "
             "them the scheduler assumes the pod needs nothing and packs the node")
    else:
        ok("cpu and memory requests and limits are all set")

    # --- security ---
    nonroot = (dig(dep, "spec", "template", "spec", "securityContext", "runAsNonRoot")
               or dig(c, "securityContext", "runAsNonRoot"))
    if nonroot is not True:
        fail("runAsNonRoot: true is not set on the pod or the container")
    else:
        ok("runAsNonRoot is set")

    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.strip().startswith("#"):
            continue
        if SECRET_RE.search(line):
            fail(f"a credential appears to be hard-coded: {line.strip()[:60]!r}. "
                 "Use env.valueFrom.secretKeyRef")
            break
    else:
        ok("no plaintext credential found")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--stage", required=True,
                    choices=["parse", "deployment", "service", "production"])
    a = ap.parse_args()

    if not a.manifest.exists():
        print(f"FAIL: no such file: {a.manifest}")
        sys.exit(1)

    docs = load(a.manifest)
    if a.stage == "parse":
        stage_parse(docs, a.manifest)
    elif docs:
        {"deployment": lambda: stage_deployment(docs),
         "service": lambda: stage_service(docs),
         "production": lambda: stage_production(docs, a.manifest)}[a.stage]()

    print()
    if FAILS:
        print(f"{len(FAILS)} problem(s) in stage '{a.stage}'")
        sys.exit(1)
    print(f"stage '{a.stage}' passed")


if __name__ == "__main__":
    main()
