# Skill: performance-reviewer

## Goal
Spot common performance anti-patterns in added code before they hit production.

---

## Inputs
- {diff_file} 鈥?path to the PR diff JSON from fetch-pr skill

---

## Steps

1. Read the diff file. Focus on added lines.

2. Scan for these patterns:

   ### Database / query patterns (CRITICAL)
   - N+1 queries: a query inside a loop
   - SELECT * with no LIMIT in production code
   - Missing index hints on large table queries

   ### Memory patterns (WARNING)
   - Loading entire file into memory instead of streaming
   - Unbounded list/array growth inside a loop
   - Large objects stored in session or global state

   ### Loop patterns (WARNING)
   - Nested loops over large collections (O(n虏) risk)
   - Repeated expensive calls inside a loop that could be cached outside
   - Array.find() or filter() called repeatedly on the same unchanged array

   ### Network patterns (WARNING)
   - Sequential awaits that could be parallelised with Promise.all()
   - Synchronous HTTP calls in Node.js
   - No timeout set on external HTTP calls

   ### Caching patterns (SUGGESTION)
   - Repeated identical function calls with same args (could be memoised)
   - No cache headers on static asset responses
   - Expensive computation run on every request with no caching

3. Skip test files.

4. Print summary.

---

## Output
Findings in memory for report-writer skill.

---

## Error Handling
- Cannot determine data sizes 鈫?note as assumption-dependent finding
