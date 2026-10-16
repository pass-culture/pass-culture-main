---
name: pr-description
description: Rédige et maintient à jour la description (et le titre) d'une Pull Request selon les conventions pass Culture. Génère une intention courte puis une liste de changements, choisit le bon template (front/back/DS/script), ajoute captures/vidéos, schémas mermaid et un score de review effort quand c'est pertinent. À utiliser dès que l'utilisateur demande d'écrire, mettre à jour, relire ou améliorer une description ou un titre de PR.
---

# PR description (pass Culture)

Objectif : produire une description de PR **agréable et rapide à relire par un humain**.
Toujours dans cet ordre : (1) l'**intention/motivation** en 1 à 3 phrases max, puis (2) la **liste des changements**.

## Workflow

1. **Récupère le contexte du diff** (ne te fie pas qu'au dernier commit) :

```bash
git fetch origin master --quiet
git log master..HEAD --pretty=format:'%h %s'          # commits de la branche (hash + sujet)
git rev-list --count master..HEAD                     # nombre de commits
git diff master...HEAD --stat                          # fichiers touchés (global)
git log master..HEAD --stat --pretty=format:'%n=== %h %s ==='  # fichiers touchés par commit
git rev-parse --abbrev-ref HEAD                        # nom de branche (ticket)
```

> Si la branche contient **plusieurs commits**, garde la correspondance commit → fichiers : elle sert à structurer la liste des changements (voir Format).

1. **Détecte le scope** à partir des chemins modifiés et choisis le template :
  - `pro/` → **front** (`template_front.md`), ticket **Jira**
  - `pro/src/design-system/` ou `pro/src/ui-kit/` majoritaire → **DS** (`template_DS.md`), ticket **Notion**
  - `api/` → **back** (`template_back.md`), ticket **Jira**
  - script/migration ponctuelle → **script** (`template_script.md`)
  - Mixte → privilégie le scope dominant et mentionne les autres dans les changements.
2. **Déduis le ticket** depuis le nom de branche (`PC-XXXXX`, `IC-XXXX`) et construis le lien Jira `https://passculture.atlassian.net/browse/PC-XXXXX`. Si rien n'est trouvé, laisse le placeholder du template.
3. **Rédige** la description (voir Format) puis **affiche-la** à l'utilisateur. **Fournis TOUJOURS la description finale dans un unique bloc de code markdown séparé** (fenced ` ```markdown `), afin qu'elle soit facilement copiable/collable telle quelle dans le champ description de la PR. Ne pousse/édite la PR (`gh pr edit`) que si l'utilisateur le demande explicitement.
4. **Mise à jour** : si une description existe déjà, conserve le template/structure, ne réécris que les sections impactées par les nouveaux changements.



## Titre de PR

Format maison (cf. historique) : `(PC-XXXXX)[SCOPE] type: courte description en anglais`

- SCOPE : `PRO` | `API` | `BO` | `DS` | `IC`
- type : `feat` | `fix` | `chore` | `refactor` | `clean` | `build` | `ci` | `docs` | `test`
- Sans ticket : préfixe `(BSR)` (Boy Scout Rule).
- Exemples réels : `(PC-42275)[PRO] feat: create exposure page`, `(BSR)[PRO] build: remove CSP rule`.



## Format de la description

> **Bloc copiable** : rends toujours la description finale dans un seul bloc de code. Comme elle contient elle-même des fences ` ``` ` (mermaid, tableaux, exemples), englobe-la dans une clôture en **4 backticks** (` ````markdown `) pour ne pas casser le rendu.

Pars du template choisi et remplis-le. Structure cible :

```markdown
## 🎯 Related Ticket or 🔧 Changes Made

[Ticket Jira](https://passculture.atlassian.net/browse/PC-XXXXX)

> Intention en 1 à 3 phrases : *pourquoi* ce changement, le problème résolu / la valeur apportée.

### 🔧 Changements
- Changement 1 (orienté « quoi » + impact, pas un dump de diff)
- Changement 2
- ...

### 🧪 Comment tester
- Étapes / commandes / résultat attendu
```

Règles de rédaction :

- **Intention d'abord, liste ensuite.** L'intention parle métier/utilisateur, pas implémentation.
- **Sépare les changements par commit** dès que la PR en contient **plusieurs** : un sous-titre par commit, avec son sujet (et son hash court), puis les changements de ce commit en dessous. Pour un **commit unique**, garde une simple liste à plat (pas de sous-titre inutile).
- **Anglais pour le code** (noms de fichiers, symboles) ; le texte narratif peut être en français comme dans l'équipe.
- **Markdown soigné** : titres, listes, tableaux, `code` inline. Emojis avec parcimonie (1 par section max).
- Si un commit regroupe beaucoup de changements hétérogènes, tu peux sous-grouper par thème à l'intérieur (ex. `Front`, `Tests`).
- Ignore les commits de bruit (merge master, `fix lint`, `wip`) : fusionne-les dans le commit pertinent ou omets-les plutôt que d'en faire une section.
- Évite le bruit : ne liste pas les changements triviaux générés (lockfiles, snapshots) sauf s'ils sont le sujet.

Exemple de liste de changements pour une PR **multi-commits** :

```markdown
### 🔧 Changements

#### `a1b2c3d` feat: add exposure page
- Nouvelle page `ExposurePage` + route associée
- Appel API `getExposure` branché sur le store

#### `d4e5f6a` test: cover exposure page
- Tests unitaires `ExposurePage.spec.tsx`
- Mock du endpoint `getExposure`
```



## Visuels (quand c'est pertinent)

Ajoute la section ci-dessous pour : changement Design System, régression visuelle corrigée, nouvelle feature produit, changement d'UX notable.

```markdown
## 🖼️ Before & After

Before | After
:---: | :---:
![before](url) | ![after](url)
```

- Vidéo/GIF pour un flow interactif. Demande les fichiers à l'utilisateur si tu ne les as pas (ne fabrique pas d'URL).
- Si tu as pris des screenshots toi-même, référence leur chemin local.



## Schémas mermaid (optionnel)

Quand un changement touche un flux, une machine à états ou une archi non triviale, ajoute un diagramme :

```markdown
\`\`\`mermaid
flowchart LR
  A[User] --> B{Eligible?}
  B -- yes --> C[Offer page]
  B -- no --> D[Fallback]
\`\`\`
```

N'en mets pas pour un changement linéaire/simple : ça doit clarifier, pas décorer.

## Sois force de proposition (inspiration CodeRabbit)

Ajoute, en fin de description, un encart synthétique quand la PR est non triviale :

```markdown
---
**🧭 Review effort : 3/5** — _raison courte (taille du diff, complexité logique, surface de test)._

**🗂️ Walkthrough**

| Fichier(s) | Résumé |
|---|---|
| `pro/src/.../Foo.tsx` | … |
| `pro/src/.../Foo.spec.tsx` | … |
```

Barème review effort (échelle 1–5) :

- **1** : trivial (renommage, copie, config).
- **2** : petit, logique localisée, bien testée.
- **3** : plusieurs fichiers, logique modérée.
- **4** : logique transverse / migration / impacts multiples.
- **5** : critique ou large surface (sécurité, paiement, archi).

Propose aussi, si pertinent : risques/points d'attention pour le relecteur, et un checklist de test ciblé. Reste concis : ces ajouts servent le relecteur, ils ne doivent pas noyer l'intention.