import { Link } from 'react-router-dom'

import fullBackIcon from 'icons/full-back.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'

import { AccessibilityLayout } from './AccessibilityLayout'
import styles from './Declaration.module.scss'

export const Declaration = () => {
  return (
    <AccessibilityLayout>
      <ButtonLink to="/accessibilite/" icon={fullBackIcon}>
        Retour vers la page Informations d’accessibilité
      </ButtonLink>
      <h1 className={styles['heading1-declaration']}>
        Déclaration d’accessibilité
      </h1>
      <p className={styles['paragraph']}>
        Le pass Culture s’engage à rendre son site internet et ses applications
        mobiles accessibles conformément à l’article 47 de la loi n° 2005-102 du
        11 février 2005.
      </p>
      <p className={styles['paragraph']}>
        À cette fin, il met en œuvre la stratégie et les actions suivantes
      </p>

      <ul>
        <li className={styles['list-item']}>
          <Link
            to="/accessibilite/schema-pluriannuel"
            className={styles['link']}
          >
            Schéma pluriannuel d’accessibilité 2024 - 2025
          </Link>
        </li>
        <li className={styles['list-item']}>
          <Link
            to="/accessibilite/schema-pluriannuel"
            className={styles['link']}
          >
            Plan d’actions 2024 - 2025
          </Link>
        </li>
      </ul>
      <p className={styles['paragraph']}>
        Cette déclaration d’accessibilité s’applique au site internet{' '}
        <a className={styles['link']} href="https://passculture.pro/">
          https://passculture.pro/
        </a>
      </p>
      <h2 className={styles['heading2']}>État de conformité</h2>
      <p className={styles['paragraph']}>
        Le site pass Culture n’est pas conforme avec le référentiel général
        d’amélioration de l’accessibilité.
      </p>
      <h3 className={styles['heading3']}>Résultat des tests</h3>
      <p className={styles['paragraph']}>
        L’audit de conformité réalisé par la DINUM révèle que :
      </p>
      <ul>
        <li className={styles['list-item']}>
          48 % des critères RGAA version 4.1 sont respectés.
        </li>
      </ul>
      <h2 className={styles['heading2']}>Contenus non accessibles</h2>
      <p className={styles['paragraph']}>
        Les contenus listés ci-dessous ne sont pas accessibles pour les raisons
        suivantes.
      </p>
      <h3 className={styles['heading3']}>Non conformité</h3>
      <ul>
        <li className={styles['list-item']}>
          Sur toutes les pages contenant le menu principal, les éléments du menu
          sortent de l’écran lorsque la largeur d’écran est réduite, que le zoom
          de la page est augmenté ou que l’écran est en mode paysage. De plus,
          quand c’est le cas, le bouton de déconnexion est invisible.
        </li>
        <li className={styles['list-item']}>
          Dans l’ensemble de l’application, les notifications suivant les
          actions ne sont pas restituées aux utilisateurs de technologies
          d’assistance.
        </li>
        <li className={styles['list-item']}>
          Sur les pages connexion, mot de passe oublié, accueil et inscription
          la technologie de recaptcha google embarque une iframe avec des
          attributs frameborder et scrolling.
        </li>
        <li className={styles['list-item']}>
          Les champs de formulaire e-mail, quantité et url ont des exemples ou
          indications de remplissage qui sont contenus uniquement dans les
          textes de substitution.
        </li>
        <li className={styles['list-item']}>
          Les champs ayant une validation du format pendant la saisie de
          l’utilisateur annoncent le message d’erreur en mode prioritaire.
        </li>
        <li className={styles['list-item']}>
          Les champs indicatif de téléphone et numéro de téléphone ont des
          intitulés cachés visuellement.
        </li>
        <li className={styles['list-item']}>
          Sur la page d’inscription, les indications de format de mot de passe
          sont cachées par défaut.
        </li>
        <li className={styles['list-item']}>
          Les messages d’erreur au niveau des groupes de cases à cocher ne sont
          pas restitués aux utilisateurs de lecteurs d’écran lorsqu’ils
          apparaissent.
        </li>
        <li className={styles['list-item']}>
          Les chemins d’étape des pages de formulaire d’offre ne permettent pas
          d’identifier l’étape active si les feuilles de styles sont
          désactivées.
        </li>
        <li className={styles['list-item']}>
          Sur la page <strong>Création d’une offre - Détail</strong> le dialog
          de modification d’image a un attribut aria-labelledby invalide et le
          champ de saisie de l’image a un attribut aria-invalid="true” par
          défaut. Par ailleurs dans le dialog, les indications de format ne sont
          pas reliées au champ de saisie de l’image.
        </li>
        <li className={styles['list-item']}>
          Dans la page <strong>Réservations / recherche réservations</strong> la
          modification des résultats de la recherche n’est pas restituée. Sur
          cette même page, les champs de dates et de type de réservation voient
          leur contenu coupé en cas de modification de l’espace entre les
          lettres. Enfin, les intitulés des champs de filtrage sont cachés
          visuellement.
        </li>
        <li className={styles['list-item']}>
          Dans le parcours d’inscription les étapes de rattachement, de
          structure, d’identification, de validation et d’activité n’ont pas une
          hiérarchie des titres cohérente.
        </li>
        <li className={styles['list-item']}>
          Dans la page <strong>Inscription - Identification</strong> les blocs
          “Nom public” et “Adresse postale” ont des informations qui ne sont pas
          reliées aux champs correspondants. Par ailleurs, sur cette page tous
          les champs de site internet et réseau social ont le même intitulé.
          Enfin, lors de l’ajout d’un nouveau champ de site internet et réseau
          social, les utilisateurs de lecteurs d’écran ne sont pas avertis.
        </li>
        <li className={styles['list-item']}>
          Dans la page <strong>Création d’une offre - Tarifs</strong>, lors de
          l’ajout d’un bloc tarif les utilisateurs de lecteurs d’écran ne sont
          pas avertis. Par ailleurs les champs relatifs à chaque tarifs ne sont
          pas regroupés. Enfin, les exemples de tarifs ne sont pas repris dans
          les messages d’erreur.
        </li>
        <li className={styles['list-item']}>
          Dans la page <strong>Création d’une offre - Dates & Capacités</strong>
          , le titre de la table n’est pas correctement associé au tableau. Sur
          cette page, les titres du dialog ne représentent pas la structure de
          la page. Par ailleurs, dans le tableau des dates, les cases à cocher
          ont des labels sans intitulé, et les champs de filtre ne sont pas
          regroupés.
        </li>
        <li className={styles['list-item']}>
          Dans les formulaires de création d’offre collective, certains champs
          ont un message d’erreur trop générique “Champ requis”.
        </li>
        <li className={styles['list-item']}>
          Dans la page{' '}
          <strong>Création d’une offre - Collective - Détail</strong>, le lien
          "Aide” ne donne pas l’information qu’il s’ouvre dans une nouvelle
          fenêtre. Dans cette même page, l’affichage de la liste de choix du
          sélecteur domaine artistique et culturel n’est pas annoncé aux
          utilisateurs de lecteurs d’écran. Ce même sélecteur ne permet pas de
          cocher les cases des options avec la touche espace du clavier. Ces
          cases à cocher ne sont pas regroupées, et n’ont pas de légende. Et
          enfin, dans ce formulaire, l’ajout d’un e-mail de notification ne
          repositionne pas l’élément actif.
        </li>
        <li className={styles['list-item']}>
          Dans la page{' '}
          <strong>Création d’une offre - Collective - Aperçu</strong>, les
          textes alternatifs des logos de l’aperçu sont non pertinents.
        </li>
      </ul>
      <h3 className={styles['heading3']}>
        Dérogations pour charge disproportionnée
      </h3>
      <ul>
        <li className={styles['list-item']}>Aucune</li>
      </ul>
      <h3 className={styles['heading3']}>
        Contenus non soumis à l’obligation d’accessibilité
      </h3>
      <ul>
        <li className={styles['list-item']}>Aucune</li>
      </ul>
      <h2 className={styles['heading2']}>
        Établissement de cette déclaration d’accessibilité
      </h2>
      <p className={styles['paragraph']}>
        Cette déclaration a été établie le 2 avril 2024.
      </p>
      <h3 className={styles['heading3']}>
        Technologies utilisées pour la réalisation du site
      </h3>
      <ul>
        <li className={styles['list-item']}>HTML5</li>
        <li className={styles['list-item']}>CSS</li>
        <li className={styles['list-item']}>JavaScript</li>
        <li className={styles['list-item']}>React</li>
      </ul>
      <h3 className={styles['heading3']}>Environnement de test</h3>
      <p className={styles['paragraph']}>
        La restitution des contenus avec les outils d’assistance a été testée
        conformément aux environnements de test suivants :
      </p>
      <a
        className={styles['link']}
        href="https://accessibilite.numerique.gouv.fr/methode/environnement-de-test/"
      >
        <p className={styles['paragraph']}>
          Plus d’information sur l’environnement de test
        </p>
      </a>
      <h3 className={styles['heading3']}>
        Les outils utilisés lors de l’évaluation
      </h3>
      <p className={styles['paragraph']}>
        L’outil le plus utilisé pour réaliser cet audit a été l’inspecteur de
        code que propose chaque navigateur. Un ensemble d’outils ont également
        été utilisés afin de s’assurer d’une restitution correcte de contenus
        accessibles dans le cas où l’examen du code seul n’a pas suffi.
      </p>
      <a
        className={styles['link']}
        href="https://accessibilite.numerique.gouv.fr/ressources/methodologie-de-test/"
      >
        <p className={styles['paragraph']}>
          Plus d’information sur les outils d’assistance
        </p>
      </a>
      <h3 className={styles['heading3']}>
        Pages du site ayant fait l’objet de la vérification de conformité
      </h3>
      <table className={styles['table']}>
        <thead>
          <tr>
            <th className={styles.th}>Titre de la page</th>
            <th className={styles.th}>URL</th>
          </tr>
        </thead>
        <tbody>
          <tr className={styles['tr']}>
            <td className={styles['td']}>Connexion</td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/connexion?de=%2F"
              >
                https://integration.passculture.pro/connexion?de=%2F
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>Mot de passe oublié</td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/demande-mot-de-passe"
              >
                https://integration.passculture.pro/demande-mot-de-passe
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>Inscription</td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/inscription"
              >
                https://integration.passculture.pro/inscription
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>Confirmation d’inscription - Merci</td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/inscription/confirmation"
              >
                https://integration.passculture.pro/inscription/confirmation
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>Accueil connecté</td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/accueil"
              >
                https://integration.passculture.pro/accueil
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>Offres / Recherche offres</td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/offres"
              >
                https://integration.passculture.pro/offres
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>Création d’une offre - Accueil</td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/offre/creation"
              >
                https://integration.passculture.pro/offre/creation
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>Création d’une offre - Détails</td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/offre/individuelle/creation/informations?offer-type=PHYSICAL_GOOD"
              >
                https://integration.passculture.pro/offre/individuelle/creation/informations?offer-type=PHYSICAL_GOOD
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>
              Réservations / recherche réservations
            </td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/parcours-inscription/structure"
              >
                https://integration.passculture.pro/parcours-inscription/structure
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>
              Création d’une offre - Stock & prix
            </td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/offre/individuelle/24200/creation/stocks"
              >
                https://integration.passculture.pro/offre/individuelle/24200/creation/stocks
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>
              Création d’une offre - Récapitulatif
            </td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/offre/individuelle/24200/creation/recapitulatif"
              >
                https://integration.passculture.pro/offre/individuelle/24200/creation/recapitulatif
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>
              Création d’une offre - Confirmation
            </td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/offre/individuelle/creation/confirmation"
              >
                https://integration.passculture.pro/offre/individuelle/creation/confirmation
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>Première connexion - Rattachement</td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/parcours-inscription/structure/rattachement"
              >
                https://integration.passculture.pro/parcours-inscription/structure/rattachement
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>Première connexion - Accueil</td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/parcours-inscription"
              >
                https://integration.passculture.pro/parcours-inscription
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>Première connexion - Structure</td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/parcours-inscription/structure"
              >
                https://integration.passculture.pro/parcours-inscription/structure
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>Inscription - Identification</td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/parcours-inscription/identification"
              >
                https://integration.passculture.pro/parcours-inscription/identification
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>Inscription - Activité</td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/parcours-inscription/activite"
              >
                https://integration.passculture.pro/parcours-inscription/activite
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>
              Création d’une offre - Collective - Détail
            </td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/offre/creation/collectif"
              >
                https://integration.passculture.pro/offre/creation/collectif
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>
              Création d’une offre - Collective - Aperçu
            </td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/offre/552/collectif/creation/apercu"
              >
                https://integration.passculture.pro/offre/552/collectif/creation/apercu
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>Inscription - Validation</td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/parcours-inscription/validation"
              >
                https://integration.passculture.pro/parcours-inscription/validation
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>Création d’une offre - Tarifs</td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/offre/individuelle/68514/creation/tarifs"
              >
                https://integration.passculture.pro/offre/individuelle/68514/creation/tarifs
              </a>
            </td>
          </tr>
          <tr>
            <td className={styles['td']}>
              Création d’une offre - Dates & Capacités
            </td>
            <td className={styles['td']}>
              <a
                className={styles['link']}
                href="https://integration.passculture.pro/offre/individuelle/68514/creation/stocks"
              >
                https://integration.passculture.pro/offre/individuelle/68514/creation/stocks
              </a>
            </td>
          </tr>
        </tbody>
      </table>
      <h2 className={styles['heading2']}>Retour d’information et contact</h2>
      <p className={styles['paragraph']}>
        Si vous avez des questions ou des remarques concernant l’accessibilité
        du site, veuillez contacter notre équipe à l’adresse suivante:&nbsp;
        <a
          className={styles['link']}
          href="mailto:accessibilite@passculture.app"
        >
          accessibilite@passculture.app
        </a>{' '}
      </p>
      <h2 className={styles['heading2']}>Voies de recours</h2>
      <p className={styles['paragraph']}>
        Cette procédure est à utiliser dans le cas suivant.
      </p>
      <p className={styles['paragraph']}>
        Vous avez signalé au responsable du site internet un défaut
        d’accessibilité qui vous empêche d’accéder à un contenu ou à un des
        services du portail et vous n’avez pas obtenu de réponse satisfaisante.{' '}
      </p>
      <ul>
        <li className={styles['list-item']}>
          Écrire un message au Défenseur des droits (
          <a
            className={styles['link']}
            href="https://formulaire.defenseurdesdroits.fr/"
          >
            Ouvrir le formulaire
          </a>
          )
        </li>
        <li className={styles['list-item']}>
          Contacter le délégué du Défenseur des droits dans votre région (
          <a
            className={styles['link']}
            href="https://www.defenseurdesdroits.fr/saisir/delegues"
          >
            Consulter l’annuaire des délégués
          </a>
          )
        </li>
        <li className={styles['list-item']}>
          Envoyer un courrier par la poste (gratuit, ne pas mettre de timbre)
          Défenseur des droits Libre réponse 71120 75342 Paris CEDEX 07
        </li>
      </ul>
    </AccessibilityLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Declaration
