import type { GetOffererResponseModel } from '@/apiClient/v1'
import { Callout } from '@/ui-kit/Callout/Callout'

import { hasOffererAtLeastOnePhysicalVenue } from '../VenueList/venueUtils'
import styles from './OffererBanners.module.scss'

export interface OffererBannersProps {
  offerer: GetOffererResponseModel | null
}

export const OffererBanners = ({ offerer }: OffererBannersProps) => {
  const hasAtLeastOnePhysicalVenue = hasOffererAtLeastOnePhysicalVenue(offerer)

  if (!offerer?.isValidated) {
    return (
      <Callout
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
          'Vos offres seront publiées sous réserve de validation de votre structure.'
        ) : (
          <>
            Nous vous invitons à créer une structure afin de pouvoir proposer
            des offres physiques ou des évènements. Vous pouvez dès à présent
            créer des offres numériques.
            <br />
            L’ensemble de ces offres seront publiées sous réserve de validation
            de votre structure.
          </>
        )}
      </Callout>
    )
  }

  if (!hasAtLeastOnePhysicalVenue) {
    return (
      <Callout
        className={styles['banner']}
        links={[
          {
            href: `https://aide.passculture.app/hc/fr/articles/4411992075281--Acteurs-Culturels-Comment-cr%C3%A9er-un-lieu-`,
            label: `En savoir plus sur la création d’une structure`,
            'aria-label':
              'Acteurs Culturels: Comment ajouter de nouveaux lieux sur votre espace et les paramétrer ? (Nouvelle fenêtre, site https://aide.passculture.app)',
            isExternal: true,
          },
        ]}
      >
        <p>
          Nous vous invitons à créer une structure, cela vous permettra ensuite
          de créer des offres physiques ou des évènements qui seront
          réservables.
        </p>
        <br />
        <p>
          Vous avez la possibilité de créer dès maintenant des offres
          numériques.
        </p>
      </Callout>
    )
  }

  return
}
