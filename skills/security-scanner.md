# Skill: security-scanner

## Goal
Deep security scan of a PR diff. Goes beyond basic code review to specifically
hunt for secrets, injection vulnerabilities, insecure patterns, and OWASP issues.

---

## Inputs
- {diff_file} - path to the PR diff JSON from fetch-pr skill
- {output_file} - optional markdown output path, usually outputs/reviews/{repo_slug}_pr{pr_number}_security-scanner.md

---

## Steps

1. Read the diff file and scan every patch for the following.
   Flag ALL matches - do not skip any.

2. CRITICAL - Hardcoded secrets (flag any line matching these patterns):
   - Strings that look like API keys: long alphanumeric strings 20+ chars assigned to a variable
   - Passwords or secrets: variable names containing password, secret, token, key, api_key, auth
     with a hardcoded string value
   - Private keys: -----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----
   - Connection strings with credentials: mongodb://, postgres://, mysql:// with user:pass@
   - AWS keys: AKIA[A-Z0-9]{16}
   - GitHub tokens: ghp_, gho_, ghu_, ghs_, ghr_

3. CRITICAL - Injection vulnerabilities:
   - SQL: string concatenation used to build a query (f"SELECT... {user_input}")
   - Command injection: os.system(), subprocess with shell=True passing user input
   - HTML/JS injection: innerHTML, document.write with unescaped user input
   - Path traversal: file paths built from user input without sanitisation

4. WARNING - Insecure patterns:
   - MD5 or SHA1 used for password hashing
   - HTTP (not HTTPS) hardcoded URLs for external services
   - debug=True or NODE_ENV=development hardcoded in non-test files
   - eval() or exec() called with dynamic input
   - Disabling SSL verification (verify=False, ssl=False, rejectUnauthorized: false)

5. SUGGESTION - Security hygiene:
   - TODO or FIXME comments near security-sensitive code
   - Logging statements that print passwords, tokens, or user PII
   - Overly broad exception handlers that swallow security errors silently

6. Save findings to {output_file} when provided, then print count of findings per severity.

---

## Output
- Markdown findings in {output_file} when provided.
- Otherwise, findings in memory for report-writer skill.

---

## Error Handling
- Binary or minified files - skip
- If no security issues found - explicitly state "No security issues detected"
