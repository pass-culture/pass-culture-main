import { addDays, isBefore } from 'date-fns'
import React from 'react'

import { DMSApplicationstatus } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { Venue } from 'core/Venue'

import NewEACInformation from '../EACInformation/NewEACInformation'

import CollectiveDmsTimeline from './CollectiveDmsTimeline/CollectiveDmsTimeline'

export interface CollectiveVenueInformationsProps {
  venue?: Venue
  isCreatingVenue: boolean
  canCreateCollectiveOffer: boolean
}

const CollectiveVenueInformations = ({
  venue,
  isCreatingVenue,
  canCreateCollectiveOffer,
}: CollectiveVenueInformationsProps) => {
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
      title={
        isCreatingVenue
          ? 'Mes informations pour les enseignants'
          : 'A destination des scolaires'
      }
      id="venue-collective-data"
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
          offererId={venue.managingOfferer.id}
        />
      )}
      {shouldEACInformationSection && (
        <NewEACInformation venue={venue} isCreatingVenue={isCreatingVenue} />
      )}
    </FormLayout.Section>
  )
}

export default CollectiveVenueInformations
