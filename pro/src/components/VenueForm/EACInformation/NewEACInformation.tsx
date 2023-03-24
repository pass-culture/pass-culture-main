import React from 'react'
import { useParams } from 'react-router-dom'

import FormLayout from 'components/FormLayout'
import { IVenue } from 'core/Venue'
import { ReactComponent as EditIcon } from 'icons/ico-pen-black.svg'
import { venueHasCollectiveInformation } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/EACInformation/utils/venueHasCollectiveInformation'
import { ButtonVariant } from 'ui-kit/Button/types'
import { ButtonLink, Title } from 'ui-kit/index'

import styles from './eacInformation.module.scss'

interface IEACInformation {
  venue?: IVenue | null
  isCreatingVenue: boolean
}
interface IEACInformationParams {
  offererId?: string | null
}

const NewEACInformation = ({ venue, isCreatingVenue }: IEACInformation) => {
  const { offererId }: IEACInformationParams = useParams()
  const collectiveDataIsNotEmpty = venue && venueHasCollectiveInformation(venue)

  return (
    <>
      <Title as="h4" level={4} className={styles['eac-title-info']}>
        Mes informations pour les enseignants
      </Title>
      <p className={styles['eac-description-info']}>
        Il s'agit d'un formulaire vous permettant de renseigner vos informations
        EAC. Les informations renseignées seront visibles par les enseignants et
        chefs d'établissement sur Adage (Application dédiée à la
        généralisation....)
      </p>
      <FormLayout.Row>
        <ButtonLink
          link={{
            to: `/structures/${offererId}/lieux/${venue?.id}/eac`,
            isExternal: false,
          }}
          Icon={collectiveDataIsNotEmpty ? EditIcon : undefined}
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
