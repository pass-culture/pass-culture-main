## Initialisation d'un utilisateur

Voici le nouveau flux d'initialisation d'un utilisateur sous le FF `WIP_SWITCH_VENUE`.

> [!CAUTION]
> Le cas des structures non-rattachées n'est pour l'instant pas traité.
> La solution la plus simple serait de retourner une propriété `isAllowed` sur la liste légère des structures.
> La liste légère des structures n'a besoin de comporter que 4 propriétés pour éviter tout risque d'exposition de données :
> - `id`: ID de la structure.
> - `publicName`: Nom public de la structure.
> - `address`: Présente si `isAllowed` est TRUE, nulle si `isAllowed` est FALSE.
> - `isAllowed`: Booléen n'indiquant que le fait qu'elle soit autorisée ou non pour cet utilisateur (sans détail sur la raison).

**Signification des emojis**
- ➖ / ➕ : Choix ou Déclaration Legacy qui va être remplacé
- 📛 : Choix ou Déclaration Legacy qui va être supprimé

### Étape 1 - Initialisation des données de l'utilisateur

```mermaid
flowchart TD

FUNCTION1("Récupération des données de l'utilisateur")
--- FUNCTION2("➖ [Espace Partenaire] Récupération de la liste des structures SEULEMENT autorisées<br>➕ [Espace Partenaire] Récupération de la liste des structures autorisées OU NON")
--- FUNCTION3("➖ [Espace Administration] Récupération de la liste des entités autorisées OU NON<br>➕ [Espace Administration] Récupération de la liste des entités SEULEMENT autorisées")
==> STEP2(("ÉTAPE 2"))
```

### Étape 2 - [Espace Partenaire] Initialisation de la structure sélectionnée

```mermaid
flowchart TD

FUNCTION1("getInitialPartnerVenueId()")
--- A{"Ai-je une structure précédemment sélectionnée<br>dans mon Local Storage ?"}
A -->|Oui| A1["Retourne cet ID de structure"]
A -->|Non| B{"N'ai-je qu'une seule structure ?"}
B -->|Oui| B1["Retourne cet ID de structure"]
B -->|Non| B0["Retourne NULL"]

A1 --> FUNCTION2
B1 --> FUNCTION2
B0 ==> STEP3

FUNCTION2("setSelectedVenueById()")
--- C{"📛 Est-ce que l'ENTITÉ PARENTE à cette structure<br>indique l'utilisateur comme onboardé ?"}
C -->|Oui| C1["📛 L'accès utilisateur est FULL"]
C -->|Non| C0["📛 L'accès utilisateur est NO-ONBOARDING"]

C1 ==> STEP3
C0 ==> STEP3

STEP3(("ÉTAPE 3"))
```

### Étape 3 - [Espace Administration] Initialisation de l'entité sélectionnée

```mermaid
flowchart TD

FUNCTION1["getInitialAdminOffererId()"]
FUNCTION1 --- A{"Ai-je une entité précédemment sélectionnée<br>dans mon Local Storage ?"}
A -->|Oui| A1["Retourne cet ID d'entité"]
A -->|Non| B{"Ai-je une structure précédemment sélectionnée<br>pour mon Espace Partenaire (ÉTAPE 2) ?"}
B -->|Oui| B1["Retourne l'ID de l'entité parente à cette structure"]
B -->|Non| C{"Ai-je au moins une structure ?"}
C -->|Oui| C1["Retourne l'ID de la première entité<br>selon l'ordre alphabétique"]
C -->|Non| C0["Retourne NULL"]

A1 --> FUNCTION2
B1 --> FUNCTION2
C1 --> FUNCTION2
C0 ==> END

FUNCTION2("setSelectedAdminOffererById()")

FUNCTION2 ==> END

END(("FIN"))
```
