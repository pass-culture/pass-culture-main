import React from 'react'

import FormLayout from 'components/FormLayout'
import { IVenue } from 'core/Venue'

import { EACInformation } from '../EACInformation'

import CollectiveDmsTimeline from './CollectiveDmsTimeline/CollectiveDmsTimeline'

export interface ICollectiveVenueInformationsProps {
  venue?: IVenue | null
  isCreatingVenue: boolean
}

const CollectiveVenueInformations = ({
  venue,
  isCreatingVenue,
}: ICollectiveVenueInformationsProps) => {
  //const isAcceptedOnAdage = venue.adageId !== null // TO FIX : venue.adageId is not yet a property of IVenue
  const isAcceptedOnAdage = false
  return (
    <FormLayout.Section
      title="A destination des scolaires"
      description={
        // istanbul ignore next: FIX ME not yet implemented
        isAcceptedOnAdage
          ? ''
          : 'Pour publier des offres à destination des scolaires, votre lieu doit être référencé sur ADAGE, la plateforme dédiée aux enseignants et aux chefs d’établissements.'
      }
    >
      {
        // istanbul ignore next: FIX ME not yet implemented
        isAcceptedOnAdage ? (
          <EACInformation venue={venue} isCreatingVenue={isCreatingVenue} />
        ) : (
          <CollectiveDmsTimeline />
        )
      }
    </FormLayout.Section>
  )
}

export default CollectiveVenueInformations
