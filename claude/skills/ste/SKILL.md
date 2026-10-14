---
name: ste
description: Write or rewrite technical text in "80% STE" (a relaxed ASD-STE100 Simplified Technical English). Use for procedures, manuals, READMEs, protocols, SOPs, how-to guides, code documentation, and when the user asks for STE or simplified or plain technical English. Do not use for papers, articles, posts, or other text for publication.
---

# 80% STE

Write technical text in a relaxed form of ASD-STE100. Follow the rules below. Where a rule makes the text unclear or unnatural, break the rule. Clarity wins.

## Scope

- **Use for:** procedures, instructions, READMEs, code comments and docstrings, explanations of code or files, summaries for the user.
- **Do not use for:** academic papers, articles, posts, introductions, or any text for publication. Write these in a natural voice with varied sentence length. If the user supplies wording, keep it (see CLAUDE.md).

## Rules

1. **One idea per sentence.**
2. **Keep sentences short.** Target 20 words or fewer for procedures and 25 or fewer for descriptions. Longer is acceptable when splitting hurts clarity.
3. **Use active voice.** Write "The script writes the file", not "The file is written by the script".
4. **Use imperative mood for steps.** Write one action per step. Put warnings and cautions before the step they apply to.
5. **One word for one meaning.** Pick one term for each concept and use it every time. Do not vary terms for style.
6. **Prefer simple verbs.** Write "use", not "utilize". Write "start", not "initiate". Write "show", not "demonstrate".
7. **Avoid phrasal verbs and idioms** when a single verb exists. Write "remove", not "take out".
8. **Keep articles** (a, an, the). Do not drop them to save words.
9. **Repeat the noun** instead of using "it", "this", or "that" when the reference could be unclear.
10. **Avoid noun stacks** of more than three nouns. Rewrite with "of", "for", or a verb.
11. **Use lists and tables** for steps, options, and parameters.
12. **Use present tense** for descriptions. Use future tense only when needed.
13. **Avoid "-ing" forms** that hide the actor or make the sentence ambiguous.
14. **Avoid ambiguous modal verbs.** "Must" means required. "Can" means possible. Avoid "should", "may", and "might" unless you mean exactly that.

## Do not simplify

Keep these as they are. Do not replace them with simpler words:

- Product names, library names, function names, file names, and commands.
- Domain terms and technical names (statistical methods, equipment, protocols).
- Numbers, units, and statistics wording that must stay exact.

## Before you finish

Check the draft:

- Any sentence over about 25 words? Split it.
- Any term that changes for the same concept? Pick one.
- Any passive sentence that hides who acts? Rewrite it.
- Did you change a domain term or product name? Restore it.
