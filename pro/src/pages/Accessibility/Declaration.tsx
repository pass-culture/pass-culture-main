import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Link } from '@/design-system/Link/Link'
import { LinkColor } from '@/design-system/Link/types'
import fullBackIcon from '@/icons/full-back.svg'

import { AccessibilityLayout } from './AccessibilityLayout'
import styles from './Declaration.module.scss'

export const Declaration = () => {
  return (
    <AccessibilityLayout mainHeading="Déclaration d’accessibilité">
      <div className={styles['page-content']}>
        <div className={styles['back-link']}>
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            to="/accessibilite/"
            icon={fullBackIcon}
            label="Retour vers la page Informations d’accessibilité"
          />
        </div>
        <p className={styles['paragraph']}>
          Le pass Culture s’engage à rendre son site internet et ses
          applications mobiles accessibles conformément à l’article 47 de la loi
          n° 2005-102 du 11 février 2005 et à l’article 16 de la loi n°2023-171
          du 9 mars 2023.
        </p>
        <p className={styles['paragraph']}>
          À cette fin, il met en œuvre la stratégie et les actions suivantes :
        </p>

        <ul>
          <li className={styles['list-item']}>
            <Link
              color={LinkColor.NEUTRAL}
              to="/schema-pluriannuel-2025-2027"
              label="Schéma pluriannuel d’accessibilité 2024 - 2025"
            />
          </li>
        </ul>
        <p className={styles['paragraph']}>
          Cette déclaration d’accessibilité s’applique au site internet{' '}
          <Link
            color={LinkColor.NEUTRAL}
            to="https://passculture.pro/"
            isExternalLink
            label="https://passculture.pro/"
          />
        </p>
        <h2 className={styles['heading2']}>État de conformité</h2>
        <p className={styles['paragraph']}>
          Le site Pass Culture – Portail Pro est non conforme avec la norme
          européenne 301 549 (v3.2.1).
        </p>
        <p className={styles['paragraph']}>
          La méthodologie d’audit se base sur le Référentiel d'Évaluation de
          l'Accessibilité Web (RAWeb 1.1), seule méthode opérationnelle publiée
          à ce jour pour vérifier l’ensemble des critères de la norme
          européenne.
        </p>
        <p className={styles['paragraph']}>
          Le site Pass Culture – Portail Pro
          (https://integration.passculture.pro/accueil) est partiellement
          conforme avec le RAWeb version 1.1 et le RGAA version 4.1, en raison
          des non-conformités énumérées dans la section « Résultats des tests ».
        </p>
        <h2 className={styles['heading2']}>Résultat des tests</h2>
        <p className={styles['paragraph']}>
          L’audit de conformité réalisé par la société Access42 révèle que le
          site est conforme à 67.65 % au RGAA version 4.1.
        </p>
        <h2 className={styles['heading2']}>Contenus inaccessibles</h2>
        <p className={styles['paragraph']}>
          Les contenus listés ci-dessous ne sont pas accessibles pour les
          raisons suivantes.
        </p>
        <h3 className={styles['heading3']}>Non conformité</h3>
        <ul>
          <li className={styles['list-item']}>
            [1.2 - RGAA] Une image de décoration au moins n'est pas ignorée des
            technologies d’assistance.
          </li>
          <li className={styles['list-item']}>
            [1.3 - RGAA] L'alternative textuelle d'une image porteuse
            d’information au moins n'est pas pertinente.
          </li>
          <li className={styles['list-item']}>
            [3.1 - RGAA] Une information au moins est véhiculée uniquement par
            la couleur.
          </li>
          <li className={styles['list-item']}>
            [5.3 - RGAA] Un tableau utilisé à des fins de présentation au moins
            n'est pas déclaré pas comme tel et/ou les contenus linéarisés de ce
            tableau ne se présentent pas dans un ordre logique dans le code
            source.
          </li>
          <li className={styles['list-item']}>
            [5.4 - RGAA] Le titre d'un tableau de données au moins n'est pas
            correctement associé au tableau.
          </li>
          <li className={styles['list-item']}>
            [5.5 - RGAA] Le titre d'un tableau de données au moins n'est pas
            pertinent.
          </li>
          <li className={styles['list-item']}>
            [5.7 - RGAA] Les en-têtes d'un tableau de données au moins ne sont
            pas correctement associés aux cellules.
          </li>
          <li className={styles['list-item']}>
            [5.8 - RGAA] Un tableau utilisé à des fins de présentation au moins
            utilise des éléments propres aux tableaux de données.
          </li>
          <li className={styles['list-item']}>
            [7.1 - RGAA] Une fonctionnalité JavaScript au moins n'est pas
            compatible avec les technologies d’assistance ou fait un usage
            inapproprié de propriétés ARIA.
          </li>
          <li className={styles['list-item']}>
            [7.5 - RGAA] Un message de statut au moins n'est pas restitué par
            les technologies d’assistance.
          </li>
          <li className={styles['list-item']}>
            [8.9 - RGAA] Une balise au moins est utilisée à des fins de
            présentation (par exemple des paragraphes vides et/ou des textes non
            structurés dans des balises de paragraphes).
          </li>
          <li className={styles['list-item']}>
            [9.1 - RGAA] La hiérarchie des titres d'une page au moins n'est pas
            pertinente.
          </li>
          <li className={styles['list-item']}>
            [9.2 - RGAA] La structure du document d'une page au moins n'est pas
            cohérente.
          </li>
          <li className={styles['list-item']}>
            [9.3 - RGAA] Une liste au moins n'est pas correctement structurée.
          </li>
          <li className={styles['list-item']}>
            [10.4 - RGAA] Un contenu au moins présente des pertes d’information
            et de lisibilité lorsque le texte est agrandi à 200%.
          </li>
          <li className={styles['list-item']}>
            [10.6 - RGAA] Un lien en environnement de texte au moins n'est pas
            suffisamment visible.
          </li>
          <li className={styles['list-item']}>
            [10.9 - RGAA] Une information au moins est véhiculée uniquement par
            la forme, la taille ou la position.
          </li>
          <li className={styles['list-item']}>
            [11.1 - RGAA] Un champ de formulaire au moins n'a pas d'étiquette.
          </li>
          <li className={styles['list-item']}>
            [11.2 - RGAA] L'étiquette d'un champ de formulaire au moins n'est
            pas pertinente.
          </li>
          <li className={styles['list-item']}>
            [11.6 - RGAA] Un regroupement de champs de formulaires au moins n'a
            pas de légende.
          </li>
          <li className={styles['list-item']}>
            [11.10 - RGAA] Le contrôle de saisie d'un champ au moins n'est pas
            pertinent (absence d'identification des champs obligatoires et/ou
            absence de présentation des formats de données attendus).
          </li>
          <li className={styles['list-item']}>
            [13.10 - RGAA] Une fonctionnalité au moins, utilisable au moyen d'un
            geste complexe, n'a pas d'alternative au moyen d'un geste simple.
          </li>
          <li className={styles['list-item']}>
            [15.1 - RAWeb] Au moins un outil d'édition ne permet de définir les
            informations d'accessibilités nécessaires à la création d'un contenu
            accessible.
          </li>
          <li className={styles['list-item']}>
            [15.3 - RAWeb] Au moins un contenu généré par une transformation des
            contenus n'est pas accessible.
          </li>
          <li className={styles['list-item']}>
            [16.2 - RAWeb] Le service d'assistance ne répond pas aux besoins de
            communication des personnes handicapées.
          </li>
        </ul>
        <h3 className={styles['heading3']}>
          Dérogations pour charge disproportionnée
        </h3>
        <ul>
          <li className={styles['list-item']}>Pas de dérogation identifiée</li>
        </ul>
        <h3 className={styles['heading3']}>
          Contenus non soumis à l’obligation d’accessibilité
        </h3>
        <ul>
          <li className={styles['list-item']}>Pas d'exemption identifiée</li>
        </ul>
        <h2 className={styles['heading2']}>
          Établissement de cette déclaration d’accessibilité
        </h2>
        <p className={styles['paragraph']}>
          Cette déclaration a été établie le 10 juillet 2026.
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
        <h3 className={styles['heading3']}>
          Agents utilisateurs, technologies d'assistance et outils utilisés pour
          vérifier l'accessibilité
        </h3>
        <p className={styles['paragraph']}>
          Les tests des pages web ont été effectués avec les combinaisons de
          navigateurs web et lecteurs d’écran suivants :
        </p>
        <ul>
          <li className={styles['list-item']}>Firefox 152 et NVDA 2025</li>
          <li className={styles['list-item']}>Firefox 152 et JAWS 2025</li>
          <li className={styles['list-item']}>
            Safari 26.5 et VoiceOver (macOS 26.5)
          </li>
          <li className={styles['list-item']}>
            Safari 26.5 et VoiceOver (iOS 26.5)
          </li>
          <li className={styles['list-item']}>
            Chrome 146 et TalkBack (Android 16)
          </li>
        </ul>
        <p className={styles['paragraph']}>
          La vérification de l’accessibilité est le résultat de tests manuels,
          assistés par des outils (feuilles CSS dédiés, extensions HeadingsMaps
          et WebDeveloper Toolbar, Color Contrast Analyser).
        </p>
        <h3 className={styles['heading3']}>
          Pages du site ayant fait l’objet de la vérification de conformité
        </h3>
        <p className={styles['paragraph']}>
          L’audit a porté sur l’échantillon de pages listé ci-dessous.
        </p>
        <table className={styles['table']}>
          <thead>
            <tr>
              <th className={styles.th}>Titre de la page</th>
              <th className={styles.th}>URL</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className={styles['td']}>Tuto de bienvenue (6 étapes)</td>
              <td className={styles['td']}>
                <Link
                  color={LinkColor.NEUTRAL}
                  to="https://passculture.pro/bienvenue"
                  isExternalLink
                  label="https://passculture.pro/bienvenue"
                />
              </td>
            </tr>
            <tr>
              <td className={styles['td']}>Inscription et validation</td>
              <td className={styles['td']}>
                <Link
                  color={LinkColor.NEUTRAL}
                  to="https://passculture.pro/inscription/compte/creation"
                  isExternalLink
                  label="https://passculture.pro/inscription/compte/creation"
                />
              </td>
            </tr>
            <tr>
              <td className={styles['td']}>Connexion</td>
              <td className={styles['td']}>
                <Link
                  color={LinkColor.NEUTRAL}
                  to="https://passculture.pro/connexion"
                  isExternalLink
                  label="https://passculture.pro/connexion"
                />
              </td>
            </tr>
            <tr>
              <td className={styles['td']}>
                Inscription structure (3 étapes et validation)
              </td>
              <td className={styles['td']}>
                <Link
                  color={LinkColor.NEUTRAL}
                  to="https://passculture.pro/inscription/structure/recherche"
                  isExternalLink
                  label="https://passculture.pro/inscription/structure/recherche"
                />
              </td>
            </tr>
            <tr>
              <td className={styles['td']}>
                Création offre réservable (parcours 3) (5 étapes et
                confirmation)
              </td>
              <td className={styles['td']}>
                <Link
                  color={LinkColor.NEUTRAL}
                  isExternalLink
                  to="https://passculture.pro/offre/creation/collectif"
                  label="https://passculture.pro/offre/creation/collectif"
                />
              </td>
            </tr>
            <tr>
              <td className={styles['td']}>
                Création offre individuelle (parcours 5) (7 étapes et
                confirmation)
              </td>
              <td className={styles['td']}>
                <Link
                  color={LinkColor.NEUTRAL}
                  isExternalLink
                  to="https://passculture.pro/offre/individuelle/creation/description"
                  label="https://passculture.pro/offre/individuelle/creation/description"
                />
              </td>
            </tr>
            <tr>
              <td className={styles['td']}>Informations bancaires</td>
              <td className={styles['td']}>
                <Link
                  color={LinkColor.NEUTRAL}
                  isExternalLink
                  to="https://passculture.pro/administration/remboursements/informations-bancaires"
                  label="https://passculture.pro/administration/remboursements/informations-bancaires"
                />
              </td>
            </tr>
            <tr>
              <td className={styles['td']}>Page d'accueil</td>
              <td className={styles['td']}>
                <Link
                  color={LinkColor.NEUTRAL}
                  isExternalLink
                  to="https://passculture.pro/accueil"
                  label="https://passculture.pro/accueil"
                />
              </td>
            </tr>
            <tr>
              <td className={styles['td']}>Les offres</td>
              <td className={styles['td']}>
                <Link
                  color={LinkColor.NEUTRAL}
                  isExternalLink
                  to="https://passculture.pro/offres"
                  label="https://passculture.pro/offres"
                />
              </td>
            </tr>
            <tr>
              <td className={styles['td']}>Les réservations</td>
              <td className={styles['td']}>
                <Link
                  color={LinkColor.NEUTRAL}
                  isExternalLink
                  to="https://passculture.pro/reservations"
                  label="https://passculture.pro/reservations"
                />
              </td>
            </tr>
            <tr>
              <td className={styles['td']}>Contenus téléchargeables</td>
              <td className={styles['td']}>
                <Link
                  color={LinkColor.NEUTRAL}
                  isExternalLink
                  to="https://passculture.pro/ecoconception/declaration"
                  label="https://passculture.pro/ecoconception/declaration"
                />
              </td>
            </tr>
            <tr>
              <td className={styles['td']}>Accessibilité</td>
              <td className={styles['td']}>
                <Link
                  color={LinkColor.NEUTRAL}
                  isExternalLink
                  to="https://passculture.pro/accessibilite/declaration"
                  label="https://passculture.pro/accessibilite/declaration"
                />
              </td>
            </tr>
            <tr>
              <td className={styles['td']}>
                Les offres réservables (collectif)
              </td>
              <td className={styles['td']}>
                <Link
                  color={LinkColor.NEUTRAL}
                  isExternalLink
                  to="https://passculture.pro/offres/collectives"
                  label="https://passculture.pro/offres/collectives"
                />
              </td>
            </tr>
            <tr>
              <td className={styles['td']}>Page d'erreur</td>
              <td className={styles['td']}>
                <Link
                  color={LinkColor.NEUTRAL}
                  isExternalLink
                  to="https://passculture.pro/xyz"
                  label="https://passculture.pro/xyz"
                />
              </td>
            </tr>
            <tr>
              <td className={styles['td']}>Plan du site</td>
              <td className={styles['td']}>
                <Link
                  color={LinkColor.NEUTRAL}
                  isExternalLink
                  to="https://passculture.pro/inscription/plan-du-site"
                  label="https://passculture.pro/inscription/plan-du-site"
                />
              </td>
            </tr>
          </tbody>
        </table>
        <h2 className={styles['heading2']}>Retour d’information et contact</h2>
        <p className={styles['paragraph']}>
          Il est important de rappeler qu’en vertu de l’article 11 de la loi de
          février 2005 :
        </p>
        <p className={styles['quote']}>
          « la personne handicapée a droit à la compensation des conséquences de
          son handicap, quels que soient l’origine et la nature de sa
          déficience, son âge ou son mode de vie. »
        </p>
        <p className={styles['paragraph']}>
          Le pass Culture s'engage à prendre les moyens nécessaires afin de
          donner accès, dans un délai raisonnable, aux informations et
          fonctionnalités recherchées par la personne handicapée, que le contenu
          fasse l'objet d'une dérogation ou non.
        </p>
        <p className={styles['paragraph']}>
          Le pass Culture invite les personnes qui rencontreraient des
          difficultés à le contacter à l'adresse&nbsp;
          <Link
            color={LinkColor.NEUTRAL}
            isExternalLink
            to="mailto:support@passculture.app"
            label="support@passculture.app"
          />
          &nbsp;afin qu’une assistance puisse être apportée (alternative
          accessible, information et contenu donnés sous une autre forme).
        </p>
        <h2 className={styles['heading2']}>Voies de recours</h2>
        <p className={styles['paragraph']}>
          Si vous constatez un défaut d'accessibilité vous empêchant d'accéder à
          un contenu ou une fonctionnalité du site, que vous nous le signalez et
          que vous ne parvenez pas à obtenir une réponse de notre part, vous
          êtes en droit de faire parvenir vos doléances ou une demande de
          saisine au Défenseur des droits.
        </p>
        <p className={styles['paragraph']}>
          Plusieurs moyens sont à votre disposition :
        </p>
        <ul>
          <li className={styles['list-item']}>
            Un&nbsp;
            <Link
              color={LinkColor.NEUTRAL}
              isExternalLink
              to="https://formulaire.defenseurdesdroits.fr/"
              label="formulaire de contact"
            />
          </li>
          <li className={styles['list-item']}>
            Un numéro de téléphone : 09 69 39 00 00
          </li>
          <li className={styles['list-item']}>
            Une adresse postale (courrier gratuit, sans affranchissement) : Le
            Défenseur des droits - Libre réponse 71120 - 75342 Paris CEDEX 07
          </li>
        </ul>
      </div>
    </AccessibilityLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Declaration
