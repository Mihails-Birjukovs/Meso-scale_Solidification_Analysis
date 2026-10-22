This folder is meant for agents to exchange handoff and report MD files between themselves to keep each other updated on project context and updates for this repo beyond info stored with commits.
Idea: each time an agent interacts with this repo and reads of modifies things, an MD file is left with context relevant to other agents that might work with the repo.
MD should be dated, and should contain info about what the agent did, the context dump, as well as agent's ID (i.e., the name of the user to whom, for instance, the ChatGPT account belongs, or a machine readable ID that help agents differentiate which one left which MD).
This MD ledger in this folder should be persistent -- MD files are not to be deleted or retroactively edited, only added when necessary.
This procedure is intended to keep different agents (or GPT instances) up to date as progress is made by different entities working on this repo.
