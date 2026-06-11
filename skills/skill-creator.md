# Skill: skill-creator

## Goal
When the agent is asked to do something and no matching skill exists,
draft a new skill file and save it to skills/pending/ for Edison to review.
The agent must NEVER use a pending skill 鈥?it must wait for approval.

---

## When to trigger this skill
Trigger this skill when:
- The user asks for a task and no skill in skills-registry.json covers it
- run search_skills.py returns no relevant match
- The user explicitly says "create a new skill for X"

Do NOT trigger this skill if an existing skill can handle the task even partially.

---

## Inputs
- {task_description} 鈥?what the user wants the agent to do
- {context} 鈥?any relevant details about the task

---

## Steps

1. Run the skill search to double-check nothing exists:
   python scripts/search_skills.py --query "{task_description}"
   If a match is returned, use that skill instead and stop.

2. Analyse the task and define the new skill:
   - What is the goal in one sentence?
   - What are the inputs?
   - What are the steps (be as specific as possible)?
   - What scripts will it need? (list them 鈥?create stubs if needed)
   - What is the output?
   - What errors should it handle?

3. Name the skill using lowercase-hyphenated format:
   e.g. dockerfile-reviewer, dependency-checker, test-generator

4. Run the creation script:
   python scripts/create_skill.py --name {skill-name} --description "{one sentence description}" --tags "{tag1},{tag2},{tag3}"

   This will:
   - Create the skill file template at skills/pending/{skill-name}.md
   - Add it to agents/skills-registry.json under "pending"

5. Open the created file and fill in all sections completely:
   - Goal
   - Inputs
   - Steps (detailed, no vague instructions)
   - Scripts needed
   - Output
   - Error handling

6. Save the completed skill file.

7. Tell Edison:
   "New skill drafted: skills/pending/{skill-name}.md
   Open it in Obsidian or any editor, review it, and move it to skills/ to activate.
   I will not use this skill until you approve it."

---

## Rules
- NEVER save new skills directly to skills/ 鈥?always skills/pending/ first
- NEVER use a skill from skills/pending/ 鈥?pending means not approved
- Always fill in every section of the skill template completely
- If a new skill needs a Python script that does not exist, create a stub
  at scripts/{script-name}.py with a TODO comment explaining what it should do

---

## Output
- skills/pending/{skill-name}.md (new skill file, awaiting approval)
- agents/skills-registry.json updated with pending entry
