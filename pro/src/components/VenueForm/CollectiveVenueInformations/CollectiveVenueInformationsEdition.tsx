import { addDays, isBefore } from 'date-fns'
import React from 'react'

import { DMSApplicationstatus } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { Venue } from 'core/Venue/types'

import { EACInformation } from '../EACInformation'

import CollectiveDmsTimeline from './CollectiveDmsTimeline/CollectiveDmsTimeline'

export interface CollectiveVenueInformationsEditionProps {
  venue?: Venue
  isCreatingVenue: boolean
  canCreateCollectiveOffer: boolean
}

export const CollectiveVenueInformationsEdition = ({
  venue,
  isCreatingVenue,
  canCreateCollectiveOffer,
}: CollectiveVenueInformationsEditionProps) => {
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
        <EACInformation venue={venue} isCreatingVenue={isCreatingVenue} />
      )}
    </FormLayout.Section>
  )
}
