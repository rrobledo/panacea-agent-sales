---
name: sparc-metodology
description: describe the steps and process for interacting with the AI.
---

## Setup Instructions

When starting a new SPARC process, create the following directory and files if they don't exist:

**Directory:** `.claude/sparc/`

**Files to create:**

### 1-specification.md
```markdown
# Specification

## Goal
<!-- What is the objective of this task/feature? -->

## Constraints
<!-- What limitations or requirements must be respected? -->

## Success Criteria
<!-- How do we know when this is done? What defines success? -->

## Context
<!-- Any relevant background information -->

## Out of Scope
<!-- What is explicitly NOT part of this task? -->
```

### 2-pseudocode.md
```markdown
# Pseudocode

## Step-by-Step Plan
<!-- Explicit steps before touching live systems -->

1.
2.
3.

## Logic Flow
<!-- Describe the logical flow of the solution -->

## Edge Cases
<!-- What edge cases need to be considered? -->

## Dependencies
<!-- What dependencies or prerequisites are needed? -->
```

### 3-architecture.md
```markdown
# Architecture

## Structure
<!-- Design the structure that best fits the plan -->

## Components
<!-- What components/modules are involved? -->

## Tooling Stack
<!-- What tools, libraries, or frameworks will be used? -->

## Data Flow
<!-- How does data move through the system? -->

## Scalability Considerations
<!-- How will this scale? -->

## Security Considerations
<!-- What security aspects need attention? -->
```

### 4-refinement.md
```markdown
# Refinement

## Implementation Progress
<!-- Track build progress in tight loops -->

### Iteration 1
- [ ] Task
- [ ] Test
- [ ] Result

## Tests
<!-- What tests validate this work? -->

## Issues Found
<!-- Document issues discovered during refinement -->

## Fixes Applied
<!-- Document fixes before moving on -->
```

### 5-completion.md
```markdown
# Completion

## Reflection
<!-- What worked well? What could be improved? -->

## Documentation
<!-- Final documentation for this work -->

## Security Audit
<!-- Security checks performed -->

- [ ] No sensitive data exposed
- [ ] Input validation in place
- [ ] Authentication/authorization verified
- [ ] Dependencies reviewed

## Quality Checks
<!-- Final quality verification -->

- [ ] Code review completed
- [ ] Tests passing
- [ ] Performance acceptable
- [ ] Edge cases handled

## Handover Notes
<!-- Information for the next person/phase -->
```

---

## Code Explanation Guidelines

When explaining code, always include:

1. **Start with an analogy**: Compare the code to something from everyday life
2. **Draw a diagram**: Use ASCII art to show the flow, structure, or relationships
3. **Walk through the code**: Explain step-by-step what happens
4. **Highlight a gotcha**: What's a common mistake or misconception?

Keep explanations conversational. For complex concepts, use multiple analogies.

---

## SPARC Framework—Project Management for AI Agents


That’s where the SPARC framework comes in. Born out of real-world pain from early agent experiments, SPARC gives every autonomous agent a lightweight “project-manager-in-a-box.” The acronym spells the agent’s day job:

Specification--Capture the goal, constraints, success criteriaâ€”in writing.
Pseudocode--Sketch an explicit step-by-step plan before touching live systems.
Architecture--Design the structure or tooling stack that best fits the plan.
Refinement--Build and test in tight loops; fix issues before moving on.
Completion--Reflect, document, run final security & quality checks, then hand over.

In other words, SPARC makes an AI agent behave like your most disciplined engineer:

Plan first (Specification + Pseudocode).
Design consciously (Architecture).
Prove every change works (Refinement’s test-driven loop).
Finish clean (Completion’s docs, audits, deployment).

Why Those Guardrails Matter

Think back to the opening horror story. Each SPARC phase kills a class of failure:

Sloppy specs? Caught in S—the agent can’t start until requirements are unambiguous.
Magical thinking? Flushed out in P—pseudocode crystalizes logic and exposes gaps.
Spaghetti solutions? Prevented in A—architecture enforces structure and scalability.
Hidden bugs? Smoked by R—nothing advances until tests go green.
Undocumented chaos or security holes? Blocked in C—the agent must write docs, run audits, and pass a final review before calling itself “done.

Result: autonomy without an ulcer.

What This Means for You

If you’re experimenting with agentic AI—AutoGPT clones, code-writing agents, multi-step data bots—adopting SPARC (or a similar discipline) is the fastest route to:

Higher reliability: agents produce work that actually runs and keeps running.
Traceability: every decision, plan, and test is logged—great for audits or debugging.
Easier collaboration: humans can jump in at any phase, knowing exactly where the agent left off.
Peace of mind: no more guessing whether your overnight agent sprint left a time-bomb in main. 

Coming Up in This Series

Over the next few posts, I will unpack each SPARC phase with practical examples, templates, and hard-won lessons:

Specification—writing a one-page brief machines (and humans) can’t misread.
Pseudocode & Planning—turning vision into executable steps.
Architecture—designing for scale, security, and maintainability.
Refinement—test-driven autonomy in action.
Completion & Reflection—why “done” means more than passing unit tests.
Case studies & ROI—real numbers from teams already using SPARC.
Strengths, gaps, and the road to SPARC 2.0.
