import { addDays, isBefore } from 'date-fns'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { IVenue } from 'core/Venue'

import NewEACInformation from '../EACInformation/NewEACInformation'

import CollectiveDmsTimeline from './CollectiveDmsTimeline/CollectiveDmsTimeline'

export interface ICollectiveVenueInformationsProps {
  venue?: IVenue
  isCreatingVenue: boolean
}

const CollectiveVenueInformations = ({
  venue,
  isCreatingVenue,
}: ICollectiveVenueInformationsProps) => {
  const shouldEACInformationSection =
    (venue?.hasAdageId &&
      venue.adageInscriptionDate &&
      isBefore(
        new Date(venue.adageInscriptionDate),
        addDays(new Date(), -30)
      )) ||
    isCreatingVenue

  return (
    <FormLayout.Section
      title="A destination des scolaires"
      description={
        venue?.hasAdageId
          ? ''
          : 'Pour publier des offres à destination des scolaires, votre lieu doit être référencé sur ADAGE, la plateforme dédiée aux enseignants et aux chefs d’établissements.'
      }
    >
      {shouldEACInformationSection && (
        <NewEACInformation venue={venue} isCreatingVenue={isCreatingVenue} />
      )}
      {!shouldEACInformationSection && venue && (
        <CollectiveDmsTimeline
          collectiveDmsApplication={venue.collectiveDmsApplication}
        />
      )}
    </FormLayout.Section>
  )
}

export default CollectiveVenueInformations
