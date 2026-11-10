---
name: jev-build
description: How Jev builds or designs a website, landing page, app or other product from a short ask ("build my friend's coffee shop website"). Plan, ask, research references, write a full brief, build, then check the result. Load before any build or design work.
---

# Build like a studio, not like a prompt box

A short ask is the start of the job, not the whole brief. Work through these steps in order.

## 1. Plan
- Write `PLAN.md` in the project folder: who it is for, the one thing a visitor should do, the pages, the content needed, the tech.
- Ask at most three questions, all at once, on what only the user knows (name, what they sell, tone, anything to avoid). If they do not answer or say "you decide", pick sensible defaults, write them in the plan and go on. Never block on a question.

## 2. Pick the tools
- Load the best installed design skill (for example world-class-design, ghost-design or ui-ux-pro-max) and the best one for the stack. One of each, not all.
- If Figma or another design tool is connected and the job would be better with it, use it and say so in one line.
- Choose the stack that suits the job (static site, TypeScript and a framework, a backend only when data must be stored). Use the structure, a README and tests that a senior engineer would expect.

## 3. Research references
- Look at the best current work for this kind of business: award galleries, Pinterest boards, component libraries such as 21st.dev, motion showcases.
- Save 3 to 6 reference screenshots in `refs/` and note in `PLAN.md` what to take from each: layout, colour, type, motion.
- References are for direction. Never copy a design, text, photo or template you have no right to use. Use free-licensed or generated assets, and write the source of each in `refs/SOURCES.md`.
- Use only the account the user is already signed in to. If a site's free limit is reached, tell the user in one line and move to another free source. Never make or switch accounts to get around a limit.

## 4. Design direction
- Decide before coding: palette (with hex values), two fonts, spacing scale, the motion language. Write it in `PLAN.md`.
- Default to rich, smooth motion: scroll-driven reveals, eased transitions, hover states, one signature moment on the first screen. Respect `prefers-reduced-motion`, keep text readable and the page fast.
- It must not look like a template. One clear idea that fits this business beats many effects.

## 5. Write the brief
- Before building, write `BRIEF.md`: the full instruction a specialist would need. Goal, audience, pages and sections, copy, design tokens, motion per section, tech and file layout, the paths of the reference images, and what "done" means.
- When a structured form helps (many sections or tokens), also write `brief.json` with the same content.
- Read the brief once as a critic and fix what is vague.

## 6. Build
- Take the role the part needs: the best designer for the look, the best front-end engineer for motion and layout, the best back-end engineer for data and security. Follow the brief.

## 7. Check your own work
- Run it. Open it in the browser, take screenshots at phone and desktop width, and compare them with the brief and the references.
- Fix what is broken, plain or off-brief, then look again. Check links, forms, the console and loading speed.
- Tell the user in a few lines what was built, where it is, how to open it, and what is not done.
