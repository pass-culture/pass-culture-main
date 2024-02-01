import React from 'react'

import { GetOffererResponseModel } from 'apiClient/v1'
import { Banner } from 'ui-kit'

import { hasOffererAtLeastOnePhysicalVenue } from '../venueUtils'

import styles from './OffererBanners.module.scss'

export interface OffererBannersProps {
  isUserOffererValidated: boolean
  offerer: GetOffererResponseModel
}

export const OffererBanners = ({
  isUserOffererValidated,
  offerer,
}: OffererBannersProps) => {
  const hasAtLeastOnePhysicalVenue = hasOffererAtLeastOnePhysicalVenue(offerer)

  if (!isUserOffererValidated) {
    return (
      <Banner
        type="notification-info"
        className={styles['banner']}
        links={[
          {
            href: `https://aide.passculture.app/hc/fr/articles/4514252662172--Acteurs-Culturels-S-inscrire-et-comprendre-le-fonctionnement-du-pass-Culture-cr%C3%A9ation-d-offres-gestion-des-r%C3%A9servations-remboursements-etc-`,
            label: 'En savoir plus',
            isExternal: true,
            'aria-label':
              'Acteurs Culturels: s’inscrire et comprendre le fonctionnement (Nouvelle fenêtre, site https://aide.passculture.app)',
          },
        ]}
      >
        <strong>
          Le rattachement à votre structure est en cours de traitement par les
          équipes du pass Culture
        </strong>
        <br />
        Un email vous sera envoyé lors de la validation de votre rattachement.
        Vous aurez alors accès à l’ensemble des fonctionnalités du pass Culture
        Pro.
      </Banner>
    )
  }

  if (!offerer.isValidated) {
    return (
      <Banner
        type="notification-info"
        className={styles['banner']}
        links={[
          {
            href: `https://aide.passculture.app/hc/fr/articles/4514252662172--Acteurs-Culturels-S-inscrire-et-comprendre-le-fonctionnement-du-pass-Culture-cr%C3%A9ation-d-offres-gestion-des-r%C3%A9servations-remboursements-etc-`,
            label: 'En savoir plus sur le fonctionnement du pass Culture',
            isExternal: true,
          },
        ]}
      >
        <strong>
          Votre structure est en cours de traitement par les équipes du pass
          Culture
        </strong>
        <br />
        {hasAtLeastOnePhysicalVenue ? (
          <>
            Toutes les offres créées à l’échelle de vos lieux seront publiées
            sous réserve de validation de votre structure.
          </>
        ) : (
          <>
            Nous vous invitons à créer un lieu afin de pouvoir proposer des
            offres physiques ou des évènements. Vous pouvez dès à présent créer
            des offres numériques.
            <br />
            L’ensemble de ces offres seront publiées sous réserve de validation
            de votre structure.
          </>
        )}
      </Banner>
    )
  }

  if (!hasAtLeastOnePhysicalVenue) {
    return (
      <Banner
        type="notification-info"
        className={styles['banner']}
        links={[
          {
            href: `https://aide.passculture.app/hc/fr/articles/4411992075281--Acteurs-Culturels-Comment-cr%C3%A9er-un-lieu-`,
            label: 'En savoir plus sur la création d’un lieu',
            'aria-label':
              'Acteurs Culturels: Comment ajouter de nouveaux lieux sur votre espace et les paramétrer ? (Nouvelle fenêtre, site https://aide.passculture.app)',
            isExternal: true,
          },
        ]}
      >
        <p>
          Nous vous invitons à créer un lieu, cela vous permettra ensuite de
          créer des offres physiques ou des évènements qui seront réservables.
        </p>
        <br />
        <p>
          Vous avez la possibilité de créer dès maintenant des offres
          numériques.
        </p>
      </Banner>
    )
  }

  return
}
