import cn from 'classnames'
import React from 'react'

import { GetVenueResponseModel } from 'apiClient/v1'
import { ReactComponent as EditIcon } from 'icons/ico-pen.svg'
import { Banner, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import CollectiveData from './CollectiveData'
import styles from './EACInformation.module.scss'
import { venueHasCollectiveInformation } from './utils/venueHasCollectiveInformation'

const EACInformation = ({
  venue,
  offererId,
  isCreatingVenue = false,
}: {
  venue: GetVenueResponseModel | null
  offererId: string
  isCreatingVenue?: boolean
}): JSX.Element => {
  const collectiveDataIsNotEmpty = venue && venueHasCollectiveInformation(venue)
  return (
    <div className="section vp-content-section" id="venue-collective-data">
      <h2 className="main-list-title">Mes informations pour les enseignants</h2>
      {collectiveDataIsNotEmpty ? (
        <CollectiveData venue={venue} />
      ) : (
        <p className={styles['description']}>
          Il s'agit d'un formulaire vous permettant de renseigner vos
          informations à destination du public scolaire. Les informations
          renseignées seront visibles par les enseignants et chefs
          d'établissement sur Adage (Application dédiée à la généralisation de
          l'éducation artistique et culturelle).
        </p>
      )}

      {isCreatingVenue && (
        <Banner type="notification-info">
          Une fois votre lieu créé, vous pourrez renseigner des informations
          pour les enseignants en revenant sur cette page.
        </Banner>
      )}

      <ButtonLink
        link={{
          to: `/structures/${offererId}/lieux/${venue?.id}/eac`,
          isExternal: false,
        }}
        variant={ButtonVariant.SECONDARY}
        isDisabled={isCreatingVenue}
        className={cn({ [styles['button']]: collectiveDataIsNotEmpty })}
      >
        {collectiveDataIsNotEmpty ? (
          <>
            <EditIcon className={styles['edit-icon']} />
            Modifier mes informations
          </>
        ) : (
          'Renseigner mes informations'
        )}
      </ButtonLink>
    </div>
  )
}

export default EACInformation
