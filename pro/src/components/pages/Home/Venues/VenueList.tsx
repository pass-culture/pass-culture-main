import React from 'react'

import Venue from 'components/pages/Home/Venues/VenueLegacy'
import { Banner } from 'ui-kit'

interface IVenueListProps {
  physicalVenues: {
    id: string
    name: string
    publicName?: string
    businessUnitId?: string
    hasReimbursementPoint: boolean
  }[]
  selectedOffererId: string
  virtualVenue: {
    id: string
    businessUnitId?: string
    hasReimbursementPoint: boolean
  } | null
}

export const VenueList = ({
  physicalVenues,
  selectedOffererId,
  virtualVenue,
}: IVenueListProps) => (
  <div className="h-venue-list">
    <Banner
      type="new"
      closable
      href={`/structures/${selectedOffererId}/lieux/${physicalVenues[0]?.id}/eac`}
      linkTitle="Renseigner vos informations "
      icon="ico-external-site-filled-white"
    >
      Nouveau ! Vous pouvez désormais renseigner les informations scolaires d'un
      lieu via votre page Lieu du pass Culture. Ces informations seront visibles
      par les enseignants sur ADAGE.
    </Banner>
    {virtualVenue && (
      <Venue
        hasBusinessUnit={!!virtualVenue.businessUnitId}
        id={virtualVenue.id}
        isVirtual
        name="Offres numériques"
        offererId={selectedOffererId}
        hasReimbursementPoint={virtualVenue.hasReimbursementPoint}
      />
    )}

    {physicalVenues?.map(venue => (
      <Venue
        hasBusinessUnit={!!venue.businessUnitId}
        id={venue.id}
        key={venue.id}
        name={venue.name}
        offererId={selectedOffererId}
        publicName={venue.publicName}
        hasReimbursementPoint={venue.hasReimbursementPoint}
      />
    ))}
  </div>
)
