import React from 'react'
import { useParams } from 'react-router-dom'

import FormLayout from 'components/FormLayout'
import { Venue } from 'core/Venue'
import { ReactComponent as FullEditIcon } from 'icons/full-edit.svg'
import { venueHasCollectiveInformation } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/EACInformation/utils/venueHasCollectiveInformation'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Banner, ButtonLink } from 'ui-kit/index'

import CollectiveData from './CollectiveData'
import styles from './eacInformation.module.scss'

interface EACInformationProps {
  venue?: Venue | null
  isCreatingVenue: boolean
}
interface EACInformationParams {
  offererId?: string | null
}

const EACInformation = ({ venue, isCreatingVenue }: EACInformationProps) => {
  const { offererId }: EACInformationParams = useParams()
  const collectiveDataIsNotEmpty = venue && venueHasCollectiveInformation(venue)

  return (
    <FormLayout.Section
      title="Mes informations pour les enseignants"
      description={
        collectiveDataIsNotEmpty
          ? ''
          : "Il s'agit d'un formulaire vous permettant de renseigner vos informations EAC. Les informations renseignées seront visibles par les enseignants et chefs d'établissement sur Adage (Application dédiée à la généralisation....)"
      }
    >
      <FormLayout.Row>
        {collectiveDataIsNotEmpty ? (
          <CollectiveData venue={venue} />
        ) : isCreatingVenue ? (
          <Banner type="notification-info">
            Une fois votre lieu créé, vous pourrez renseigner des informations
            pour les enseignants en revenant sur cette page.
          </Banner>
        ) : (
          <></>
        )}
      </FormLayout.Row>
      <FormLayout.Row>
        <ButtonLink
          link={{
            to: `/structures/${offererId}/lieux/${venue?.id}/eac`,
            isExternal: false,
          }}
          Icon={collectiveDataIsNotEmpty ? FullEditIcon : undefined}
          variant={ButtonVariant.SECONDARY}
          isDisabled={isCreatingVenue}
          className={styles['edit-button']}
        >
          {collectiveDataIsNotEmpty
            ? 'Modifier mes informations'
            : 'Renseigner mes informations'}
        </ButtonLink>
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
export default EACInformation
