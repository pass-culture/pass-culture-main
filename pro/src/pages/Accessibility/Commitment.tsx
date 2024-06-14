import { Link } from 'react-router-dom'

import fullBackIcon from 'icons/full-back.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'

import { AccessibilityLayout } from './AccessibilityLayout'
import styles from './Commitment.module.scss'

export const Commitment = () => {
  return (
    <AccessibilityLayout>
      <ButtonLink
        link={{
          to: '/accessibilite/',
        }}
        icon={fullBackIcon}
      >
        Retour vers la page Informations d’accessibilité
      </ButtonLink>
      <h1 className={styles['heading1-commitment']}>
        Les engagements du pass Culture pour l’accessibilité numérique
      </h1>
      <p className={styles['paragraph']}>
        <i>Date de publication : 21 mai 2024</i>
      </p>
      <p className={styles['paragraph']}>
        Le pass Culture est né de la volonté de mettre à disposition des jeunes
        un nouveau dispositif favorisant l’accès à la culture afin de renforcer
        et diversifier les pratiques culturelles, en révélant la richesse
        culturelle des territoires. En d’autres termes, le pass Culture a pour
        vocation de rendre accessible la culture à une population qui est
        souvent empêchée par de multiples freins. Le pass Culture s’appuie sur
        la longue histoire des politiques françaises de démocratisation de la
        culture pour rapprocher tous les usagers des acteurs culturels, quelle
        que soit leur situation.
      </p>
      <p className={styles['paragraph']}>
        Le choix d’une politique publique matérialisée par un produit numérique
        nous oblige à envisager cette question également sous le prisme de l’
        accessibilité numérique.
      </p>
      <p className={styles['paragraph']}>
        Le pass Culture s’inscrit ainsi dans la continuité des politiques
        publiques d’inclusion numérique. Tout d’abord en s’appuyant sur les
        initiatives existantes tournées vers l’illettrisme numérique, vers
        l’engagement du “non-public”, la mise à disposition d’équipements
        numériques et plus globalement la médiation numérique. Nous travaillons
        également à l’adaptation du service aux personnes en situation de
        handicap, qu’il s’agissent des jeunes bénéficiaires de cette politique
        ou des acteurs culturels.
      </p>
      <p className={styles['paragraph']}>
        À cet égard et afin de pérenniser la démarche, un groupe de travail
        transversal a été créé en interne. Il est composé de personnes en lien
        avec les publics, d’ingénieurs en informatique, de designeurs, de
        sociologues et de personnes dédiées à la conception du produit.
      </p>
      <h2 className={styles['heading2-commitment']}>
        L’inclusion au coeur de la stratégie technique{' '}
      </h2>
      <p className={styles['paragraph']}>
        Deux audits évaluant l’accessibilité de la version web du pass Culture
        ont déjà été conduits en 2020 et 2022 pour permettre de rendre compte et
        d’évaluer le travail effectué. Fin 2023 et début 2024, le travail s’est
        poursuivi sur le site à destination des acteurs culturels.
      </p>
      <p className={styles['paragraph']}>
        Nous prenons en compte dans nos développements la compatibilité avec un
        maximum de versions de système d’exploitation ou de modèles de
        téléphone. Cependant, nous recommandons aux utilisateurs en situation de
        handicap d’utiliser les dernières versions de notre application, de leur
        navigateur, de leur système d’exploitation et des logiciels
        d’assistance.
      </p>
      <p className={styles['paragraph']}>
        Ce travail pour rendre et maintenir accessibles les parcours clé de
        l’application web est le socle pour construire un environnement
        numérique inclusif et ainsi initier des échanges dédiés avec les acteurs
        du monde de l’accessibilité et utilisateurs en situation de handicap.
      </p>
      <h2 className={styles['heading2-commitment']}>
        Collaboration et sensibilisation
      </h2>
      <p className={styles['paragraph']}>
        Au-delà de la technologie utilisée, les acteurs culturels avec lesquels
        nous travaillons sont sensibilisés à la question de l’accessibilité. Ils
        ont l’obligation d’indiquer si leur lieu et leurs offres sont
        accessibles selon une nomenclature faisant référence aux différentes
        catégories de handicap. L’implication des acteurs culturels dans notre
        démarche d’accessibilité est évidemment essentielle à la dimension
        inclusive de l’ensemble du dispositif pass Culture et, <i>in fine</i> ,
        à l’accès de tous les jeunes à la culture. En 2024, ce travail a été
        prolongé avec la mise en place d’un partenariat technologique avec
        <a className={styles['link']} href="https://acceslibre.beta.gouv.fr/">
          {''} acceslibre {''}
        </a>
        afin d’enrichir plus largement les informations d’accessibilité des
        lieux tout en contribuant à ce projet qui dépasse le pass Culture et qui
        vise à rendre faciliter l’accès pour les personnes en situation de
        handicap. Un filtre dédié a également été ajouté dans la recherche du
        site à destination des jeunes bénéficiaires. Ce filtre permet aux jeunes
        bénéficiaires d’identifier facilement les établissements qui proposent
        un accueil adapté.
      </p>
      <p className={styles['paragraph']}>
        D’autres évolutions sont prévues dans les prochains mois et sont
        disponibles sur le {''}
        <Link className={styles['link']} to="/accessibilite/schema-pluriannuel">
          Schéma pluriannuel d’accessibilité 2024 - 2025
        </Link>
        {''} et le {''}
        <a
          className={styles['link']}
          href="https://passculture.app/accessibilite/plan-d-actions"
        >
          Schéma pluriannuel d’accessibilité 2022 - 2024
        </a>
      </p>
      <p className={styles['paragraph']}>
        Au delà de ces premiers aspects, le rôle des aidants et des structures
        d’accompagnement est primordial pour garantir une bonne information
        auprès des publics en situation de handicap et éventuellement fournir un
        appui nécessaire aux moins autonomes. Ainsi, nous sommes en contact avec
        certains grands réseaux nationaux à travers lesquels nous diffusons de
        l’information sur le pass Culture. Notre volonté est d’être le plus
        possible au contact des structures et des professionnels pour leur
        donner les moyens d’accompagner leurs publics mais également pour être à
        l’écoute des retours des utilisateurs.
      </p>
      <p className={styles['paragraph']}>
        Ces retours utilisateurs nourrirons alors le travail de nos équipes pour
        continuer à adapter le pass Culture aux usages de l’ensemble de nos
        utilisateurs. L’accessibilité est toujours une histoire en mouvement.
        Vous trouverez d’ailleurs dans le schéma pluriannuel les chantiers sur
        lesquels nous travaillons à ce niveau. Si vous avez des retours au sujet
        de notre traitement, n’hésitez pas à écrire à {''}
        <a
          className={styles['link']}
          href="mailto:accessibilite@passculture.app"
        >
          accessibilite@passculture.app
        </a>
      </p>
      <p className={styles['paragraph']}>
        <a
          className={styles['link']}
          href="https://aide.passculture.app/hc/fr/sections/4597468688924-Situation-de-handicap"
        >
          Vous pouvez retrouver également toutes nos fiches d’aide pour vous
          inscrire sur le pass Culture directement dans notre centre d’aide.
        </a>
      </p>
    </AccessibilityLayout>
  )
}
// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Commitment
