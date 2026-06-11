# Skill: docker-reviewer

## Goal
Review Dockerfile and docker-compose changes for security issues,
best practices violations, and image size problems.

---

## Inputs
- {diff_file} 鈥?path to the PR diff JSON from fetch-pr skill

---

## Steps

1. Read the diff file. Look for Dockerfile, docker-compose.yml,
   docker-compose.yaml, .dockerfile files in files_changed.
   If none found, print "No Docker files changed" and stop.

2. For each Docker file changed, scan added lines for:

   ### CRITICAL 鈥?Security
   - Running as root: no USER instruction before CMD/ENTRYPOINT
   - Secrets in ENV or ARG: ENV PASSWORD=, ARG API_KEY=
   - ADD used instead of COPY (ADD can fetch remote URLs unexpectedly)
   - curl | bash or wget | sh patterns (piping remote scripts)
   - Privileged mode in docker-compose: privileged: true

   ### WARNING 鈥?Best practices
   - Using :latest tag (non-deterministic builds)
   - Multiple RUN apt-get install without --no-install-recommends
   - Not combining RUN commands (creates unnecessary layers)
   - COPY . . before installing dependencies (busts cache unnecessarily)
   - No HEALTHCHECK defined for long-running services
   - Exposed unnecessary ports (exposing 22/SSH in a web service)

   ### SUGGESTION 鈥?Image hygiene
   - Not cleaning apt cache: apt-get clean && rm -rf /var/lib/apt/lists/*
   - Dev dependencies installed in production image
   - No .dockerignore file referenced or visible in the PR
   - Base image not pinned to a digest (FROM node:18 vs FROM node:18@sha256:...)

3. Print summary per file.

---

## Output
Findings in memory for report-writer skill.

---

## Error Handling
- No Docker files in diff 鈫?stop cleanly with notice
