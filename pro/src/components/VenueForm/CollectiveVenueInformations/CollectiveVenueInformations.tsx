import { addDays, isBefore } from 'date-fns'
import React from 'react'

import { DMSApplicationstatus } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { IVenue } from 'core/Venue'

import NewEACInformation from '../EACInformation/NewEACInformation'

import CollectiveDmsTimeline from './CollectiveDmsTimeline/CollectiveDmsTimeline'

export interface ICollectiveVenueInformationsProps {
  venue?: IVenue
  isCreatingVenue: boolean
  canCreateCollectiveOffer: boolean
}

const CollectiveVenueInformations = ({
  venue,
  isCreatingVenue,
  canCreateCollectiveOffer,
}: ICollectiveVenueInformationsProps) => {
  const hasAdageIdForMoreThan30Days = Boolean(
    venue?.hasAdageId &&
      venue?.adageInscriptionDate &&
      isBefore(new Date(venue?.adageInscriptionDate), addDays(new Date(), -30))
  )
  const shouldEACInformationSection =
    hasAdageIdForMoreThan30Days ||
    ((!venue?.adageInscriptionDate || !venue?.collectiveDmsApplication) &&
      canCreateCollectiveOffer) ||
    isCreatingVenue

  const hasRefusedDmsApplication =
    venue?.collectiveDmsApplication?.state === DMSApplicationstatus.REFUSE ||
    venue?.collectiveDmsApplication?.state === DMSApplicationstatus.SANS_SUITE

  return (
    <FormLayout.Section
      title="A destination des scolaires"
      id="for-schools"
      description={
        venue?.hasAdageId ||
        canCreateCollectiveOffer ||
        hasRefusedDmsApplication
          ? ''
          : 'Pour publier des offres à destination des scolaires, votre lieu doit être référencé sur ADAGE, la plateforme dédiée aux enseignants et aux chefs d’établissements.'
      }
    >
      {venue?.collectiveDmsApplication && (
        <CollectiveDmsTimeline
          collectiveDmsApplication={venue.collectiveDmsApplication}
          hasAdageId={venue.hasAdageId}
          hasAdageIdForMoreThan30Days={hasAdageIdForMoreThan30Days}
          adageInscriptionDate={venue.adageInscriptionDate}
        />
      )}
      {shouldEACInformationSection && (
        <NewEACInformation venue={venue} isCreatingVenue={isCreatingVenue} />
      )}
    </FormLayout.Section>
  )
}

export default CollectiveVenueInformations
