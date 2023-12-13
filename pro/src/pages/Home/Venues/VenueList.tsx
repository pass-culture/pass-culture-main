import React from 'react'

import { GetOffererVenueResponseModel } from 'apiClient/v1'
import { getLastCollectiveDmsApplication } from 'utils/getLastCollectiveDmsApplication'

import Venue from './Venue'
import styles from './Venue.module.scss'

interface VenueListProps {
  physicalVenues: GetOffererVenueResponseModel[]
  selectedOffererId: number
  virtualVenue: GetOffererVenueResponseModel | null
  offererHasBankAccount: boolean
  hasNonFreeOffer: boolean
}

const VenueList = ({
  physicalVenues,
  selectedOffererId,
  virtualVenue,
  offererHasBankAccount,
  hasNonFreeOffer,
}: VenueListProps) => {
  const offererHasCreatedOffer =
    virtualVenue?.hasCreatedOffer ||
    physicalVenues.some((venue) => venue.hasCreatedOffer)
  const indexLastPhysicalVenues = physicalVenues.length - 1
  return (
    <div className={styles['venue-list']}>
      {virtualVenue && (
        <Venue
          venueId={virtualVenue.id}
          isVirtual
          name="Offres numériques"
          offererId={selectedOffererId}
          hasMissingReimbursementPoint={
            virtualVenue.hasMissingReimbursementPoint
          }
          venueHasCreatedOffer={virtualVenue.hasCreatedOffer}
          offererHasCreatedOffer={offererHasCreatedOffer}
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
          hasNonFreeOffer={hasNonFreeOffer}
          isFirstVenue={true}
        />
      )}

      {physicalVenues?.map((venue, index) => (
        <Venue
          venueId={venue.id}
          key={selectedOffererId + '-' + venue.id}
          name={venue.name}
          offererId={selectedOffererId}
          publicName={venue.publicName}
          hasMissingReimbursementPoint={venue.hasMissingReimbursementPoint}
          offererHasCreatedOffer={offererHasCreatedOffer}
          venueHasCreatedOffer={venue.hasCreatedOffer}
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
          hasNonFreeOffer={hasNonFreeOffer}
          isFirstVenue={index === indexLastPhysicalVenues}
        />
      ))}
    </div>
  )
}

export default VenueList
