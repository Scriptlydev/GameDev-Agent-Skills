# GameDev Agent Skills — Présentation française

**Statut actuel : documentation et conception uniquement.** Aucun des 30 skills n'est annoncé comme fonctionnel.

But : bâtir une collection open source de **30 skills** compatibles avec les agents qui lisent le standard `SKILL.md`, répartis en **Godot (8), Unity (8), Blender (8), Universels (6)**.

Notre avantage doit venir de **chaînes de travail vérifiables** : analyse, validation, correction proposée, approbation humaine si une écriture est nécessaire, tests, compte rendu et possibilité de revenir en arrière.

**Ne pas confondre :** un MCP expose les fonctionnalités d'un logiciel à l'IA ; un skill guide l'agent pour mener une tâche de bout en bout. Notre dépôt n'a pas besoin de copier des serveurs MCP existants.

### Lire en premier

- [Cahier des charges](docs/PRD.md)
- [Catalogue des 30 skills](docs/SKILL_CATALOG.md)
- [Feuille de route](docs/IMPLEMENTATION_PLAN.md)
- [Première tâche Claude Code](docs/FIRST_TASK_FOR_CLAUDE.md)
- [État du projet](STATE.md)

**Attention à Godot :** le serveur `hi-godot/godot-ai` version 4 demande Godot 4.7+. Pour un projet en 4.5.1, privilégier d'abord une voie CLI/headless en lecture seule ou un adaptateur alternatif dont la compatibilité a été vérifiée sur la version exacte.
