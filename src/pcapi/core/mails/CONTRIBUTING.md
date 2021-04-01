# Envoyer des mails dans pcapi

L'envoi de mails se fait via la fonction
`pcapi.core.mails.send(recipients, data)`.

`data` est un dictionnaire, généralement créé par une fonction définie
dans un sous-module de `pcapi.emails` :

```python
def get_frobulation_mail_data(user):
    return {
        "MJ-TemplateID": 123456,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "first_name": user.firstName,
        },
    }

def notify_user_frobulation(user):
    data = get_frobulation_mail_data(user)
    return pcapi.core.mails.send(recipients=[user.email], data=data)
```

En cas de succès comme d'échec, les données du mail sont sauvegardées
en base de données via le modèle `pcapi.core.mails.models.Email`.


## Format des données pour les modèles Mailjet

Le contexte à injecter dans les modèles (*templates*) Mailjet est à
définir dans un dictionnaire sous la clé "Vars". On peut y mettre :

- des chaînes de caractères comme le nom de l'offre... ;
- des booléens commençant par `is_` **sous forme d'entier** ;
- des dates sous forme de chaîne de caractères ;
- des prix sous forme de chaîne de caractères ;
- des identifiants "humanisés" sous forme de chaîne de caractères.


## Backends

Selon l'environnement, un backend approprié est choisi, défini par
`settings.EMAIL_BACKEND` (et surchargeable via la variable
d'environnement du même nom) :

- sur la production, les mails sont envoyés via Mailjet
  (cf. `MailjetBackend`) ;

- sur les environnements testing et staging, les mails sont également
  envoyés via Mailjet, mais les destinataires originaux sont remplacés
  par l'adresse mail définie dans `DEV_EMAIL_ADDRESS`, ceci afin de ne
  pas envoyer de mail à des adresses réelles, notamment sur staging
  (cf. `ToDevMailjetBackend`) ;

- en test, aucun mail n'est envoyé : on en stocke simplement une
  représentation en mémoire dans une liste
  (`pcapi.core.mails.testing.outbox`) ;

- en local, aucun mail n'est envoyé : on logge (INFO) seulement les
  données des mails.

Pour effectuer des tests de charge et éviter de polluer ou "encombrer"
Mailjet, il convient donc de surcharger `EMAIL_BACKEND` et de choisir
le backend `pcapi.core.mails.backends.logger.LoggerBackend`.


## Vérifier l'envoi de mails dans les tests automatisés

Le backend de test stocke une représentation des mails en mémoire dans
la liste `pcapi.core.mails.testing.outbox`. On peut donc vérifier
l'envoi des mails ainsi :

```python
import pcapi.core.mails.testing as mails_testing

def test_frobulation():
    user = UserFactory()

    frobulate(user)

    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["Vars"]["first_name"] == user.firstName
```


## Envoyer des mails via l'API Mailjet en local

Définissez les variables d'environnement suivantes :

- `EMAIL_BACKEND="pcapi.core.mails.backends.mailjet.ToDevMailjetBackend"` ;
- `SUPPORT_EMAIL_ADDRESS` : c'est l'adresse de l'émetteur, qui doit
  avoir été validée par Mailjet. Le plus simple est d'utiliser la même
  adresse que sur les environnements de testing, staging ou prod ;
- `DEV_EMAIL_ADDRESS="votre_adresse_personnelle"` : l'adresse à
  laquelle tout mail sera envoyé (quelle soit le destinataire
  original).
- `MAILJET_API_KEY` et `MAILJET_API_SECRET`.


Si le mail n'est pas reçu, regarder en bas du dashboard de Mailjet pour plus ample informations.
