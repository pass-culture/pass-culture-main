# Assistant pro (Culturo)

Culturo est l'assistant IA du portail pro : un partenaire culturel pose une question,
Claude répond en quelques phrases et propose des pages du portail et des articles du centre
d'aide. Il est activé par le feature flag `WIP_ENABLE_PRO_ASSISTANT` et servi par
`POST /assistant/messages` (`routes/pro/pro_assistant.py`).

## Ce qui est envoyé à Claude

Chaque question envoie une requête à l'API Claude (`connectors/pro_assistant.py`) :

| Partie               | Contenu                                                                                  | Source                       | Tokens (14/10/2026) |
| -------------------- | ---------------------------------------------------------------------------------------- | ---------------------------- | ------------------- |
| `system`, bloc 1     | Règles : rôle, périmètre, format de réponse                                              | `prompt.RULES`               | 1 360               |
| `system`, bloc 2     | Pages du portail : `route_id`, titre, chemin, usage, prérequis                           | `portal_map.py`              | 2 551               |
| `system`, bloc 2     | Articles du centre d'aide                                                                | `knowledge/help_center.json` | ~259 000            |
| `system`, bloc 2     | Nouveautés du portail (optionnel, absent pour l'instant)                                 | `knowledge/nouveautes.md`    | 0                   |
| `messages`           | Tours précédents, conservés dans Redis (`conversation_store.py`)                         |                              | 0 au 1er tour       |
| `messages`, `user`   | La question, avec les données personnelles remplacées par des marqueurs (`redaction.py`) |                              | ~20                 |
| `messages`, `system` | Contexte anonyme : page actuelle et indicateurs oui/non (`context.py`)                   |                              | 207                 |

Total pour une première question : 263 178 tokens, dont 98,5 % d'articles du centre d'aide.

La partie `system` (règles et base de connaissances) est identique pour tous les utilisateurs
et mise en cache par l'API Claude : le point de cache est à la fin du bloc 2, avec le TTL de
`PRO_ASSISTANT_CACHE_TTL` (`5m` ou `1h`). La relire depuis le cache coûte environ 0,05$ par
question ; l'écrire quand le cache est froid coûte environ 1,32$ (`5m`) ou 2,11 $ (`1h`).

Deux conséquences :

- la partie `system` doit rester identique octet pour octet d'une requête à l'autre : n'y
  mettez jamais de date, d'identifiant ni de donnée utilisateur, les données propres à
  l'utilisateur vont dans `messages` ;
- elle est générée une seule fois par processus (`knowledge.render_knowledge_base()` est mis
  en cache) : un processus API en cours d'exécution n'utilise les nouveaux fichiers de
  connaissances qu'après un redémarrage (un déploiement s'en charge).

## Sources de la base de connaissances

Rien n'est téléchargé au moment de répondre : la base de connaissances est un export figé,
versionné dans ce dossier.

| Fichier                             | Contenu                                                                                                                                                                                               | Comment le mettre à jour                                                   |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `knowledge/help_center.json`        | Les 135 articles des deux catégories « Acteurs culturels » du centre d'aide public (https://aide.passculture.app)                                                                                     | Généré par `flask build_pro_assistant_knowledge`, jamais modifié à la main |
| `portal_map.py`                     | Les 23 pages du portail vers lesquelles l'assistant peut renvoyer. C'est aussi la liste blanche des liens : Claude ne renvoie que des `route_id`, et le serveur en déduit les libellés et les chemins | Modifié à la main, à partir de `pro/src/app/AppRouter/`                    |
| `knowledge/nouveautes.md`           | Nouveautés récentes du portail (optionnel)                                                                                                                                                            | Export Markdown manuel de la base Notion « Nouveautés »                    |
| `prompt.CONTACT_SUPPORT_ARTICLE_ID` | Article du centre d'aide proposé quand l'assistant ne peut pas répondre                                                                                                                               | Modifié à la main                                                          |

Quand une source n'est pas rafraîchie après un changement :

- article modifié : Culturo répond avec l'ancien contenu ;
- article supprimé : Culturo peut encore le proposer, et le lien peut être cassé ;
- nouvel article : Culturo ne le connaît pas ;
- route du portail renommée : le bouton « Aller à la page » mène à une page inexistante.

## Rafraîchir la base de connaissances

### Articles du centre d'aide

Dans la stack locale, `src/` est synchronisé de votre clone vers le conteneur `pc-api`, mais
pas dans l'autre sens : la commande écrit le fichier dans le conteneur, il faut donc le
recopier ensuite. Lancez les commandes depuis la racine du dépôt.

1. Récupérez les articles depuis l'API publique Zendesk Help Center (aucun identifiant
   nécessaire) :

   ```bash
   docker exec pc-api flask build_pro_assistant_knowledge
   docker cp pc-api:/usr/src/app/src/pcapi/core/pro_assistant/knowledge/help_center.json \
     api/src/pcapi/core/pro_assistant/knowledge/help_center.json
   ```

   Les brouillons sont ignorés, le HTML est converti en texte et les articles sont triés par
   identifiant, pour qu'un même contenu donne toujours le même fichier. La commande affiche
   ensuite la taille de la base de connaissances et son nombre de tokens : exact avec le
   backend Anthropic (`PRO_ASSISTANT_BACKEND=pcapi.connectors.pro_assistant.AnthropicBackend`,
   le comptage des tokens est gratuit), estimé avec le backend de test.
   `--skip-fetch` affiche seulement la taille des fichiers actuels.

2. Relisez le diff de `knowledge/help_center.json` : articles ajoutés, supprimés et modifiés,
   et taille de la base de connaissances.

3. Vérifiez que l'article de contact du support existe toujours (la commande affiche `1`) :

   ```bash
   grep -c '"id": "13171848152348"' api/src/pcapi/core/pro_assistant/knowledge/help_center.json
   ```

   S'il a été supprimé, choisissez un autre article et mettez à jour
   `prompt.CONTACT_SUPPORT_ARTICLE_ID`.

4. Redémarrez l'API (`docker restart pc-api`) et lancez l'évaluation (voir plus bas).

5. Commitez et déployez. La première question après le déploiement écrit la nouvelle base de
   connaissances dans le cache, une seule fois.

Les catégories sont listées dans `knowledge_builder.HELP_CENTER_CATEGORY_IDS`.

### Pages du portail

Quand une route du portail pro change (`pro/src/app/AppRouter/routesMap.tsx`,
`pro/src/app/AppRouter/routes/*.tsx`), mettez à jour la `PortalPage` correspondante dans
`portal_map.py` : `path` pour le lien, `related_paths` pour détecter la page où se trouve
l'utilisateur, `description` et `prerequisites` pour Claude. Une nouvelle `PortalPage` est
automatiquement ajoutée au prompt, à la liste blanche et aux `route_ids` autorisés dans la
réponse.

Lancez ensuite les tests (`pytest tests/core/pro_assistant`) et l'évaluation.

### Nouveautés du portail

Exportez la base Notion « Nouveautés » en Markdown, gardez les 18 à 24 derniers mois, les
plus récentes en premier, et enregistrez le résultat dans `knowledge/nouveautes.md`. Suivez
ensuite les étapes 2 à 5 ci-dessus.

## Évaluation

```bash
docker exec pc-api flask run_pro_assistant_eval
docker exec pc-api flask run_pro_assistant_eval --case-id news --case-id who-are-you
```

Les 41 cas de `evals/questions.json` sont envoyés au backend configuré. Le rapport donne la
part de bonnes pages proposées, les questions hors sujet détectées, les fuites de données
personnelles (doit valoir 0), les requêtes servies depuis le cache et le coût. Avec le
backend Anthropic, le jeu complet coûte environ 4 $. Lancez-la après chaque modification des
règles, de la base de connaissances ou du modèle.
