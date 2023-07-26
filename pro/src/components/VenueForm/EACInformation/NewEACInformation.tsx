import React from 'react'
import { useParams } from 'react-router-dom'

import FormLayout from 'components/FormLayout'
import { Venue } from 'core/Venue/types'
import fullEditIcon from 'icons/full-edit.svg'
import { venueHasCollectiveInformation } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/EACInformation/utils/venueHasCollectiveInformation'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Banner, ButtonLink, Title } from 'ui-kit/index'

import styles from './eacInformation.module.scss'

interface EACInformationProps {
  venue?: Venue | null
  isCreatingVenue: boolean
}
interface EACInformationParams {
  offererId?: string | null
}

const NewEACInformation = ({ venue, isCreatingVenue }: EACInformationProps) => {
  const { offererId }: EACInformationParams = useParams()
  const collectiveDataIsNotEmpty = venue && venueHasCollectiveInformation(venue)

  return (
    <>
      {!isCreatingVenue && (
        <Title as="h4" level={4} className={styles['eac-title-info']}>
          Mes informations pour les enseignants
        </Title>
      )}
      <p className={styles['eac-description-info']}>
        Il s'agit d'un formulaire vous permettant de renseigner vos informations
        EAC. Les informations renseignées seront visibles par les enseignants et
        chefs d'établissement sur Adage (Application dédiée à la
        généralisation....)
      </p>
      {isCreatingVenue && (
        <Banner type="notification-info">
          Une fois votre lieu créé, vous pourrez renseigner des informations
          pour les enseignants en revenant sur cette page.
        </Banner>
      )}

      <FormLayout.Row>
        <ButtonLink
          link={{
            to: `/structures/${offererId}/lieux/${venue?.id}/eac`,
            isExternal: false,
          }}
          icon={collectiveDataIsNotEmpty ? fullEditIcon : undefined}
          variant={ButtonVariant.SECONDARY}
          isDisabled={isCreatingVenue}
          className={styles['edit-button']}
        >
          {collectiveDataIsNotEmpty
            ? 'Modifier mes informations pour les enseignants'
            : 'Renseigner mes informations pour les enseignants'}
        </ButtonLink>
      </FormLayout.Row>
    </>
  )
}
export default NewEACInformation
