import React from 'react'

import { GetOffererVenueResponseModel } from 'apiClient/v1'
import { getLastCollectiveDmsApplication } from 'utils/getLastCollectiveDmsApplication'

import Venue from './Venue'

interface VenueListProps {
  physicalVenues: GetOffererVenueResponseModel[]
  selectedOffererId: number
  virtualVenue: GetOffererVenueResponseModel | null
  offererHasBankAccount: boolean
}

const VenueList = ({
  physicalVenues,
  selectedOffererId,
  virtualVenue,
  offererHasBankAccount,
}: VenueListProps) => {
  return (
    <div className="h-venue-list">
      {virtualVenue && (
        <Venue
          venueId={virtualVenue.id}
          isVirtual
          name="Offres numériques"
          offererId={selectedOffererId}
          hasMissingReimbursementPoint={
            virtualVenue.hasMissingReimbursementPoint
          }
          hasCreatedOffer={virtualVenue.hasCreatedOffer}
          dmsInformations={getLastCollectiveDmsApplication(
            virtualVenue.collectiveDmsApplications
          )}
          hasAdageId={virtualVenue.hasAdageId}
          hasProvider={virtualVenue.hasVenueProviders}
          adageInscriptionDate={virtualVenue.adageInscriptionDate}
          hasPendingBankInformationApplication={
            virtualVenue.hasPendingBankInformationApplication
          }
          demarchesSimplifieesApplicationId={
            virtualVenue.demarchesSimplifieesApplicationId
          }
          offererHasBankAccount={offererHasBankAccount}
        />
      )}

      {physicalVenues?.map((venue) => (
        <Venue
          venueId={venue.id}
          key={selectedOffererId + '-' + venue.id}
          name={venue.name}
          offererId={selectedOffererId}
          publicName={venue.publicName}
          hasMissingReimbursementPoint={venue.hasMissingReimbursementPoint}
          hasCreatedOffer={venue.hasCreatedOffer}
          dmsInformations={getLastCollectiveDmsApplication(
            venue.collectiveDmsApplications
          )}
          hasProvider={venue.hasVenueProviders}
          hasAdageId={venue.hasAdageId}
          adageInscriptionDate={venue.adageInscriptionDate}
          hasPendingBankInformationApplication={
            venue.hasPendingBankInformationApplication
          }
          demarchesSimplifieesApplicationId={
            venue.demarchesSimplifieesApplicationId
          }
          offererHasBankAccount={offererHasBankAccount}
        />
      ))}
    </div>
  )
}

export default VenueList
