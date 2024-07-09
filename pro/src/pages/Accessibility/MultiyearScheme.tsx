import fullBackIcon from 'icons/full-back.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'

import { AccessibilityLayout } from './AccessibilityLayout'
import styles from './MultiyearScheme.module.scss'

export const MultiyearScheme = () => {
  return (
    <AccessibilityLayout>
      <ButtonLink to="/accessibilite/" icon={fullBackIcon}>
        Retour vers la page Informations d’accessibilité
      </ButtonLink>
      <h1 className={styles['heading1-scheme']}>
        Schéma pluriannuel d’accessibilité 2024 - 2025
      </h1>
      <h2 className={styles['heading2']}>INTRODUCTION</h2>
      <p className={styles['paragraph']}>
        L’article 47 de la loi n° 2005-102 du 11 février 2005 pour l’égalité des
        droits et des chances, la participation et la citoyenneté des personnes
        rend obligatoire à tout service de communication publique en ligne
        d’être accessible à tous.
      </p>
      <h2 className={styles['heading2']}>
        DÉFINITION DE L’ACCESSIBILITÉ NUMÉRIQUE
      </h2>
      <p className={styles['paragraph']}>
        L’accessibilité numérique permet d’accéder aux contenus (sites web,
        documents bureautiques, supports multimédias, intranets d’entreprise,
        applications mobiles…), quelle que soit sa façon de naviguer.
      </p>
      <p className={styles['paragraph']}>
        <strong>
          L’accessibilité numérique est indispensable aux personnes en situation
          de handicap pour :
        </strong>
      </p>
      <ul>
        <li className={styles['list-item']}>s’informer ;</li>
        <li className={styles['list-item']}>communiquer ;</li>
        <li className={styles['list-item']}>
          accomplir des démarches administratives ;
        </li>
        <li className={styles['list-item']}>
          mener une activité professionnelle…
        </li>
      </ul>
      <p className={styles['paragraph']}>
        L’accessibilité numérique profite à tous : aux personnes âgées, aux
        personnes en situation de handicap temporaire ou permanent, aux
        personnes peu à l’aise avec Internet…
      </p>
      <p className={styles['paragraph']}>
        L’accessibilité numérique s’inscrit dans une démarche d’égalité et
        constitue un enjeu politique et social fondamental afin de garantir à
        tous, sans discrimination, le même accès à l’information et aux services
        en ligne.
      </p>
      <p className={styles['paragraph']}>
        L’accessibilité numérique est un domaine transverse qui concerne toutes
        les personnes impliquées dans la création, la maintenance et
        l’utilisation des dispositifs numériques : décideurs, chefs de projet,
        graphistes, développeurs, producteurs de contenus.
      </p>
      <h2 className={styles['heading2']}>POLITIQUE D’ACCESSIBILITÉ</h2>
      <p className={styles['paragraph']}>
        L’accessibilité numérique est au cœur des préoccupations liées au
        développement ou à la mise à disposition de sites web ou d’applications
        tant auprès du public que des personnels internes de la SAS pass
        Culture.
      </p>
      <p className={styles['paragraph']}>
        Cette volonté s’illustre par l’élaboration de ce schéma pluriannuel
        d’accessibilité numérique associé à des plans annuels d’action, dans
        l’objectif d’accompagner la mise en conformité RGAA (Référentiel Général
        d’Amélioration de l’Accessibilité) et l’amélioration progressive des
        sites web et applications concernés.
      </p>
      <p className={styles['paragraph']}>
        L’élaboration, le suivi et la mise à jour de ce schéma pluriannuel sont
        placés sous la responsabilité du pôle Accessibilité.
      </p>
      <p className={styles['paragraph']}>
        <strong>Ses missions sont de :</strong>
      </p>
      <ul>
        <li className={styles['list-item']}>
          promouvoir l’accessibilité par la diffusion des normes et des bonnes
          pratiques ;
        </li>
        <li className={styles['list-item']}>
          accompagner les équipes internes par des actions notamment de
          formation ;
        </li>
        <li className={styles['list-item']}>
          contrôler et veiller à l’application de la loi n° 2005-102 du 11
          février 2005 en procédant à des audits réguliers ;
        </li>
        <li className={styles['list-item']}>
          assurer la prise en charge des demandes des utilisateurs et de manière
          générale la qualité du service rendu aux utilisateurs en situation de
          handicap ;
        </li>
        <li className={styles['list-item']}>
          faire une veille sur les évolutions réglementaires.
        </li>
      </ul>
      <h2 className={styles['heading2']}>
        RESSOURCES HUMAINES ET FINANCIÈRES AFFECTÉES À L’ACCESSIBILITÉ NUMÉRIQUE
      </h2>
      <p className={styles['paragraph']}>
        Le pilotage et le suivi de la conformité au RGAA reviennent au pôle
        Accessibilité. Cette équipe transverse est notamment composée de
        personnes en lien avec les publics, d’ingénieurs en informatique, de
        designeuses, et de personnes dédiées à la conception du produit.{' '}
      </p>
      <h2 className={styles['heading2']}>
        ORGANISATION DE LA PRISE EN COMPTE DE L’ACCESSIBILITÉ NUMÉRIQUE
      </h2>
      <p className={styles['paragraph']}>
        <strong>
          La prise en compte de l’accessibilité numérique nécessite :
        </strong>
      </p>
      <ul>
        <li className={styles['list-item']}>
          de poursuivre l’adaptation de l’organisation interne de production et
          de gestion des sites web et application concernés ;
        </li>
        <li className={styles['list-item']}>
          de poursuivre l’accompagnement des équipes ;
        </li>
        <li className={styles['list-item']}>
          de veiller à la prise en compte de l’accessibilité dans les procédures
          de marché ;
        </li>
        <li className={styles['list-item']}>
          de prendre en charge des personnes en situation de handicap
          lorsqu’elles signalent des difficultés.
        </li>
      </ul>
      <p className={styles['paragraph']}>
        Les éléments ci-dessous décrivent les points importants sur lesquels la
        SAS pass Culture s’appuiera pour améliorer l’accessibilité numérique de
        l’ensemble de ses sites web et applications.
      </p>
      <p className={styles['paragraph']}>
        <strong>Action de formation et de sensibilisation</strong>
      </p>
      <p className={styles['paragraph']}>
        Tout au long de la période d’application de ce schéma, des actions de
        formation et de sensibilisation vont être organisées. Elles permettront
        aux personnels intervenant sur les sites, les applications mais aussi
        sur les supports de communication de développer, éditer et mettre en
        ligne des contenus accessibles.
      </p>
      <p className={styles['paragraph']}>
        <strong>Plus précisément, notre action consiste à :</strong>
      </p>
      <ul>
        <li className={styles['list-item']}>
          sensibiliser pour bien faire comprendre l’importance du respect des
          règles de bonnes pratiques d’accessibilité numérique ;
        </li>
        <li className={styles['list-item']}>
          former pour acquérir les bonnes pratiques indispensables pour produire
          des sites et applications accessibles (graphisme, ergonomie,
          développement) et publier des contenus accessibles.
        </li>
      </ul>
      <p className={styles['paragraph']}>
        <strong>Recours à des compétences externes</strong>
      </p>
      <p className={styles['paragraph']}>
        Chaque fois que nécessaire, la SAS pass Culture fait appel à des
        intervenants externes afin de l’accompagner dans la prise en compte de
        l’accessibilité. Cela recouvre par exemple les actions de
        sensibilisation et de formation, les actions d’accompagnements et plus
        particulièrement les actions d’audits et de certification des sites web
        et applications concernés.
      </p>
      <p className={styles['paragraph']}>
        <strong>
          Prise en compte de l’accessibilité numérique dans les projets
        </strong>
      </p>
      <p className={styles['paragraph']}>
        Les objectifs d’accessibilité et de conformité au RGAA sont inscrits et
        rappelés dès le début des projets dont ils constitueront un axe majeur
        et une exigence de base. De la même manière, ces objectifs et ces
        exigences sont rappelés dans les éventuelles conventions établies avec
        nos partenaires. Comme pour le RGPD, l’accessibilité est citée dans la
        réflexion préalable et nécessaire à l’engagement des projets.
      </p>
      <p className={styles['paragraph']}>
        Pour favoriser la prise en compte de l’accessibilité numérique dans les
        projets, des composants normés, des modèles accessibles et une
        documentation dédiée et évolutive sont mis à la disposition des équipes
        projets.
      </p>
      <p className={styles['paragraph']}>
        <strong>Tests utilisateurs</strong>
      </p>
      <p className={styles['paragraph']}>
        Si des tests utilisateurs sont organisés, en phase de conception, de
        validation ou d’évolution d’un site web ou d’une application, le panel
        d’utilisateurs constitué comprendra dans toute la mesure du possible des
        personnes en situation de handicap. Le Conseil national consultatif des
        personnes handicapées accompagne en particulier le pass Culture sur
        cette dimension.
      </p>
      <p className={styles['paragraph']}>
        <strong>
          Prise en compte de l’accessibilité dans les procédures de marchés
        </strong>
      </p>
      <p className={styles['paragraph']}>
        L’accessibilité numérique et la conformité au RGAA sont prises en compte
        et participent à l’évaluation de la qualité de l’offre d’un prestataire
        lors de la commande de travaux au travers des appels d’offres notamment.
      </p>
      <p className={styles['paragraph']}>
        Les procédures d’élaboration des marchés ainsi que les règles
        d’évaluation des candidatures sont adaptées pour davantage prendre en
        compte les exigences de conformité au RGAA.
      </p>
      <p className={styles['paragraph']}>
        <strong>Recrutement</strong>
      </p>
      <p className={styles['paragraph']}>
        Une attention particulière est portée sur les compétences en matière
        d’accessibilité numérique des personnels intervenant sur les services
        numériques, lors de la création des fiches de postes et les procédures
        de recrutement.
      </p>
      <p className={styles['paragraph']}>
        <strong>Traitement des retours utilisateurs</strong>
      </p>
      <p className={styles['paragraph']}>
        Conformément aux dispositions prévues par le RGAA et aux attentes
        légitimes des utilisateurs, un moyen de contact est mis en place : les
        demandes sont traitées par le pôle Support (contact –{' '}
        <a
          className={styles['link']}
          href="mailto:accessibilite@passculture.app"
        >
          accessibilite@passculture.app
        </a>
        ),
      </p>
      <p className={styles['paragraph']}>
        en étroite collaboration avec le pôle Accessibilité, responsable de
        l’élaboration, la mise en place et le suivi de ce schéma pluriannuel.
      </p>
      <p className={styles['paragraph']}>
        <strong>Processus de contrôle et de validation</strong>
      </p>
      <p className={styles['paragraph']}>
        Chaque site ou application fera l’objet lors de la mise en ligne
        initiale, lors d’une mise à jour substantielle, d’une refonte ou à la
        fin des opérations de mises aux normes, d’un contrôle permettant
        d’établir une déclaration de conformité conformément aux termes de la
        loi. Ces opérations de contrôles, réalisées en interne ou par
        l’intermédiaire de prestataires spécialisés, destinés à l’établissement
        ou la mise à jour des déclarations de conformité interviennent en
        complément des opérations habituelles de recette et contrôles
        intermédiaires qui sont organisées tout au long de la vie des projets.
      </p>
      <h2 className={styles['heading2']}>PÉRIMÈTRE TECHNIQUE ET FONCTIONNEL</h2>
      <p className={styles['paragraph']}>
        <strong>Recensement</strong>
      </p>
      <p className={styles['paragraph']}>
        Ce schéma pluriannuel ne concerne que le site
        <a className={styles['link']} href="https://passculture.pro/">
          {''} https://passculture.pro/
        </a>
      </p>
      <p className={styles['paragraph']}>
        Vous pouvez retrouver le plan annuel général incluant l’ensemble des
        sites gérés par le pass Culture à l’adresse suivante:
        <a className={styles['link']} href="https://passculture.fr/">
          {''} https://passculture.fr/
        </a>
      </p>
      <p className={styles['paragraph']}>
        <strong>Évaluation et qualification</strong>
      </p>
      <p className={styles['paragraph']}>
        Chaque site ou application a été qualifié selon des critères tels que :
      </p>
      <ul>
        <li className={styles['list-item']}>la fréquentation,</li>
        <li className={styles['list-item']}>le service rendu,</li>
        <li className={styles['list-item']}>la criticité,</li>
        <li className={styles['list-item']}>
          le cycle de vie (date de la prochaine refonte),
        </li>
        <li className={styles['list-item']}>les technologies employées.</li>
      </ul>
      <p className={styles['paragraph']}>
        Des évaluations rapides de l’accessibilité, permettant de servir de
        socle à l’élaboration des interventions d’audits ont été ou vont être
        réalisées sur l’ensemble des sites et applications concernés.
      </p>
      <p className={styles['paragraph']}>
        Ces évaluations portent sur un petit nombre de critères choisis pour
        leur pertinence en termes d’évaluation de la complexité et la
        faisabilité de la mise aux normes RGAA.
      </p>
      <p className={styles['paragraph']}>
        L’annexe 1 (infra : « Annexe 1 : périmètre technique et fonctionnel
        public ») décrit les éléments pouvant être rendus publics du périmètre
        technique et fonctionnel. En effet, certaines applications peuvent ne
        pas être rendues publiques pour des raisons de sécurité ou de
        confidentialité par exemple.
      </p>
      <p className={styles['paragraph']}>
        <strong>Agenda planifié des interventions</strong>
      </p>
      <p className={styles['paragraph']}>
        Compte tenu des informations recueillies lors de l’élaboration de ce
        schéma, la complexité des sites et applications, leur classement par
        ordre de priorité et leur évaluation en termes de faisabilité, les
        opérations de mise en conformité vont s’étaler sur les années 2024 à
        2025 et au-delà.
      </p>
      <p className={styles['paragraph']}>
        <strong>Plans annuels</strong>
      </p>
      <p className={styles['paragraph']}>
        Ce schéma pluriannuel sera accompagné de plans annuels d’actions qui
        décriront en détail les opérations mises en œuvre pour prendre en charge
        l’ensemble des besoins en termes d’accessibilité numérique de la SAS
        pass Culture.
      </p>
      <h2 className={styles['heading2']}>
        ANNEXE 1 : PÉRIMÈTRE TECHNIQUE ET FONCTIONNEL
      </h2>
      <p className={styles['paragraph']}>
        Site à destination des acteurs culturels :{' '}
        <a className={styles['link']} href="https://passculture.pro/">
          https://passculture.pro/
        </a>
      </p>
      <h3 className={styles['heading3']}>Plan annuel 2024</h3>
      <ul>
        <li className={styles['list-item']}>
          Mise en place d’un pied de page et d’un plan de site - Réalisé
        </li>
        <li className={styles['list-item']}>
          Mise en place d’un partenariat avec le site accesslibre - Réalisé
        </li>
        <li className={styles['downlist-item']}>
          pour mettre à disposition des acteurs culturels et des jeunes
          bénéficiaires les données d’accessibilité des lieux
        </li>
        <li className={styles['downlist-item']}>
          pour mettre aux acteurs culturels de compléter directement les
          informations d’accessibilité de leur établissement dans acceslibre
          afin d’en mutualiser l’usage
        </li>
        <li className={styles['list-item']}>
          Réalisation d’un audit externe par la DINUM - Réalisé
        </li>
        <li className={styles['downlist-item']}>
          les améliorations suite à l’audit porteront sur les erreurs bloquantes
          ou majeures - En cours
        </li>
        <li className={styles['list-item']}>
          Publication de la déclaration d’accessibilité - Réalisé
        </li>
        <li className={styles['list-item']}>
          Organisation d’une journée dédiée à l’accessibilité à destination des
          équipes techniques et produit - Réalisé
        </li>
        <li className={styles['list-item']}>
          Modification de l’ensemble des pages du site pour qu’elles s’adaptent
          à la taille de l’écran (responsivité) - En cours
        </li>
        <li className={styles['list-item']}>
          Mise en place d’un design système respectant le RGAA avec un objectif
          AAA - En cours
        </li>
        <li className={styles['list-item']}>
          Reprise de l’ensemble des composants pour les rendre accessibles - En
          cours
        </li>
        <li className={styles['list-item']}>
          Formation continue des équipes techniques et produit - En cours{' '}
        </li>
        <li className={styles['list-item']}>
          Mise en place d’un standard de développement visant à ne développer
          que des nouvelles fonctionnalités respectant l’ensemble des critères
          du RGAA - En cours
        </li>
        <li className={styles['list-item']}>
          Mise en place d’une formation initiale à l’accessibilité pour les
          nouveaux arrivants de l’équipe technique et produit - A faire
        </li>
      </ul>
      <h3 className={styles['heading3']}>Plan annuel 2025</h3>
      <ul>
        <li className={styles['list-item']}>
          Mise en place de modalités d’accessibilité au niveau des offres afin
          que les partenaires culturels puissent indiquer les moyens mis en
          oeuvre pour rendre leurs propositions accessibles
        </li>
        <li className={styles['list-item']}>
          Résolution des derniers critères non respectés selon l’audit réalisé
          en 2024
        </li>
        <li className={styles['list-item']}>
          Réalisation d’un nouvel audit d’accessibilité
        </li>
      </ul>
    </AccessibilityLayout>
  )
}
// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = MultiyearScheme
