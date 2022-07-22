# Envoyer des mails dans pcapi 

L'envoi de mails se fait via la fonction
`pcapi.core.mails.send(recipients, data)`.

`data` est une dataclasse de type SendinblueTransactionalEmailData ou SendinblueTransactionalWithoutTemplateEmailData
, généralement créé par une fonction définie dans un sous-module de `pcapi.core.mails.transactionals` :

```python
def get_frobulation_email_data(user) -> SendinblueTransactionalEmailData:
    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.ACCEPTED_AS_BENEFICIARY.value,
        params={
            "CREDIT": int(user.deposit.amount), 
        },
    )

def send_frobulation_email(user) -> bool:
    data = get_frobulation_email_data(user)
    return pcapi.core.mails.send(recipients=[user.email], data=data)
```

En cas de succès comme d'échec, les données du mail sont sauvegardées
en base de données via le modèle `pcapi.core.mails.models.Email`.


## Format des données pour les modèles Sendinblue

SendinblueTransactionalEmailData est utilisé pour les emails qui ont un template Sendinblue listé dans 
`pcapi.core.mails.transactional.sendinblue_template_ids.TransactionalEmail`

Un template possède les attributs suivants: 
```python
@dataclasses.dataclass
class Template:
    id_prod: int
    id_not_prod: int
    tags: list[str] = dataclasses.field(default_factory=list)
    use_priority_queue: bool = False
    sender: SendinblueTransactionalSender = SendinblueTransactionalSender.SUPPORT
```
id_prod = id du template Sendinblue en production
id_not_prod = id du template Sendinblue en testing et staging (même compte Sendinblue)
tags = permet de filtrer les emails côtés dashboard Sendinblue -> les tags issues du code sont prioritaires sur ceux définis dans Sendinblue
use_priority_queue = avec ce paramètre on peut définir ce template comme prioritaire (à utiliser pour les emails type inscription utilisateur)

Le contexte à injecter dans les modèles (*templates*) Sendinblue est à
définir dans un dictionnaire sous la clé "params" de la dataclasse "SendinblueTransactionalEmailData". On peut y mettre :
- les variables dans params sont définies en MAJUSCULE (par convention)
- des chaînes de caractères comme le nom de l'offre... ;
- des booléens commençant par `IS_` **sous forme de booléens python (True ou False)** ;
- des dates sous forme de chaîne de caractères ;
- des prix sous forme de float ou chaîne de caractères (Sendinblue accepte les deux);


SendinblueTransactionalWithoutTemplateEmailData, est un format pour les emails avec un sujet, 
contenu html et/ou pièces jointes

## Backends
Selon l'environnement, un backend approprié est choisi, défini par
`settings.EMAIL_BACKEND` (et surchargeable via la variable
d'environnement du même nom) :

- sur la production, les mails sont envoyés via SendinBlue
  (cf. `pcapi.core.mails.backends.sendinblue.SendinblueBackend`) ;

- sur les environnements testing et staging, les mails sont également
  envoyés via SendinBlue, mais les destinataires originaux sont remplacés
  par l'adresse mail définie dans `DEV_EMAIL_ADDRESS`, ceci afin de ne
  pas envoyer de mail à des adresses réelles, notamment sur staging
  (cf. `ToDevSendinblueBackend`) ;

- en test, aucun mail n'est envoyé : on en stocke simplement une
  représentation en mémoire dans une liste
  (`pcapi.core.mails.testing.outbox`) ;

- en local, aucun mail n'est envoyé : on logge (INFO) seulement les
  données des mails.

Pour effectuer des tests de charge et éviter de polluer ou "encombrer"
Sendinblue, il convient donc de surcharger `EMAIL_BACKEND` et de choisir
le backend `pcapi.core.mails.backends.logger.LoggerBackend`.


## Vérifier l'envoi de mails dans les tests automatisés

Le backend de test stocke une représentation des mails en mémoire dans
la liste `pcapi.core.mails.testing.outbox`. On peut donc vérifier
l'envoi des mails ainsi :

```python
import pcapi.core.mails.testing as mails_testing

def test_frobulation():
    user = UserFactory()

    send_frobulation_email(user)

    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["params"]["FIRSTNAME"] == user.firstName
```


## Envoyer des mails via l'API Sendinblue en local
Définissez les variables d'environnement suivantes :

- `EMAIL_BACKEND="pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend"` ;
- `SUPPORT_EMAIL_ADDRESS` : c'est l'adresse de l'émetteur, qui doit
  avoir été validée par Sendinblue. Le plus simple est d'utiliser la même
  adresse que sur les environnements de testing, staging ou prod ;
- `DEV_EMAIL_ADDRESS="votre_adresse_personnelle"` : l'adresse à
  laquelle tout mail sera envoyé (quelle soit le destinataire
  original);
- `SENDINBLUE_API_KEY`


Si le mail n'est pas reçu, regarder le dashboard de Sendinblue (section 'Transactional > Logs') pour plus ample informations.


