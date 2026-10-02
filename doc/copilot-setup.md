## Configurer Copilot pour générer les descriptions de PR 🤖

### Pourquoi

- La description est le point d'entrée du relecteur : intention, changements, comment tester, visuels.
- Le skill [`pr-description`](../.agents/skills/pr-description/SKILL.md) applique automatiquement nos conventions (titre, ticket Jira, structure, récapitulatif par fichier). Il suit le standard ouvert [Agent Skills](https://agentskills.io).
- GitHub Copilot est l'outil utilisé chez pass Culture : il détecte le skill automatiquement, sans configuration dans le projet.

### 1. Installer Copilot

1. Installe [VS Code](https://code.visualstudio.com/).
2. Installe l'extension **GitHub Copilot Chat** si elle n'est pas déjà présente.
3. Connecte-toi avec ton compte GitHub de l'organisation pass Culture.
4. Obtiens une licence Copilot : <!-- TODO: add the pass Culture Copilot license request process -->

### 2. Vérifier la configuration

1. Ouvre le dossier racine du repo dans VS Code.
2. Ouvre **Copilot Chat** et passe en mode **Agent** (nécessaire pour qu'il lance les commandes `git`).
3. Tape `/` : `pr-description` doit apparaître dans la liste.

### 3. Générer la description

1. Sur ta branche, lance `/pr-description` (tu peux ajouter du contexte : `/pr-description le but est de …`).
2. Copilot analyse les changements par rapport à `master`, déduit le ticket depuis le nom de branche et propose :
   - un **titre** au format `(PC-XXXXX)[scope] (type): summary` (voir le [format du titre de PR](./pull-request.md))
   - une **description** dans un bloc markdown à copier
3. Colle la description dans la PR **à la place du modèle**, et le titre dans le champ titre.
4. Ajoute tes **captures d'écran / vidéos** à la main (Copilot ne peut pas les envoyer sur GitHub).

Pour **mettre à jour** une description existante, relance `/pr-description` en collant la description actuelle : seules les sections concernées par les nouveaux commits sont réécrites.

### 4. Dépannage

| Problème                                 | Solution                                                                                                        |
| :--------------------------------------- | :-------------------------------------------------------------------------------------------------------------- |
| `pr-description` n'apparaît pas avec `/` | Vérifie que le dossier ouvert est bien la racine du repo, puis mets à jour VS Code et l'extension Copilot Chat. |
| Le mode **Agent** n'est pas disponible   | Vérifie que ta licence Copilot est active sur ton compte GitHub pass Culture.                                   |
| Copilot ne lance pas les commandes git   | Accepte l'exécution des commandes dans le terminal quand Copilot te le demande.                                 |

### Erreurs à éviter

- Coller la description sans la relire : l'intention doit refléter le vrai besoin métier.
- Oublier les visuels pour un changement d'interface.
- Laisser le texte du modèle dans la PR.

### Annexe : autres outils

| Outil       | Détection du skill                           | Lancement                                                             |
| :---------- | :------------------------------------------- | :-------------------------------------------------------------------- |
| Cursor      | Automatique (`.agents/skills/`)              | `/pr-description` en mode **Agent**                                   |
| Claude Code | ⚠️ Pas encore (ne lit que `.claude/skills/`) | « Suis les instructions de `.agents/skills/pr-description/SKILL.md` » |

> Claude Code : en attendant la prise en charge de `.agents/skills/`, tu peux aussi créer un lien symbolique local, non versionné :
>
> ```bash
> mkdir -p .claude/skills
> ln -s ../../.agents/skills/pr-description .claude/skills/pr-description
> echo ".claude/skills/pr-description" >> .git/info/exclude
> ```

### Ressources

- [Format du titre de PR](./pull-request.md)
- [Modèle de description manuel](../.github/pull_request_template/manual.md)