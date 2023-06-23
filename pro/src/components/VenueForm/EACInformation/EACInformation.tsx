import React from 'react'
import { useParams } from 'react-router-dom'

import FormLayout from 'components/FormLayout'
import { IVenue } from 'core/Venue'
import { ReactComponent as FullEdit } from 'icons/full-edit.svg'
import { venueHasCollectiveInformation } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/EACInformation/utils/venueHasCollectiveInformation'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Banner, ButtonLink } from 'ui-kit/index'

import CollectiveData from './CollectiveData'
import styles from './eacInformation.module.scss'

interface IEACInformation {
  venue?: IVenue | null
  isCreatingVenue: boolean
}
interface IEACInformationParams {
  offererId?: string | null
}

const EACInformation = ({ venue, isCreatingVenue }: IEACInformation) => {
  const { offererId }: IEACInformationParams = useParams()
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
            to: `/structures/${offererId}/lieux/${venue?.nonHumanizedId}/eac`,
            isExternal: false,
          }}
          Icon={collectiveDataIsNotEmpty ? FullEdit : undefined}
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
