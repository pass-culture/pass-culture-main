import React, { useEffect, useState } from 'react'

import Venue from 'components/pages/Home/Venues/Venue'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import { ReactComponent as WhitePenIcon } from 'icons/ico-external-site-filled-white.svg'
import InternalBanner from 'ui-kit/Banners/InternalBanner'

interface IVenueListProps {
  physicalVenues: {
    id: string
    name: string
    publicName?: string
    businessUnitId?: string
    hasMissingReimbursementPoint: boolean
  }[]
  selectedOffererId: string
  virtualVenue: {
    id: string
    businessUnitId?: string
    hasMissingReimbursementPoint: boolean
  } | null
}

export const VenueList = ({
  physicalVenues,
  selectedOffererId,
  virtualVenue,
}: IVenueListProps) => {
  const [displayVenueCollectiveDataBanner, setDisplayCollectiveDataBanner] =
    useState(false)

  useEffect(() => {
    canOffererCreateCollectiveOfferAdapter(selectedOffererId).then(response =>
      setDisplayCollectiveDataBanner(
        response.payload.isOffererEligibleToEducationalOffer &&
          physicalVenues.length > 0
      )
    )
  }, [selectedOffererId])

  const bannerLocation =
    physicalVenues.length === 1
      ? {
          pathname: `/structures/${selectedOffererId}/lieux/${physicalVenues[0]?.id}`,
          state: { scrollToElementId: 'venue-collective-data' },
          search: '?fromBanner=true',
        }
      : undefined

  return (
    <div className="h-venue-list">
      {displayVenueCollectiveDataBanner && (
        <InternalBanner
          type="new"
          to={bannerLocation}
          linkTitle="Renseigner ces informations"
          Icon={WhitePenIcon}
          closable
          handleOnClick={() => setDisplayCollectiveDataBanner(false)}
        >
          Nouveau ! Vous pouvez désormais renseigner les informations de votre
          lieu, à destination des enseignants, depuis votre page Lieu du pass
          Culture. Ces informations seront visibles par les enseignants sur
          Adage.
        </InternalBanner>
      )}
      {virtualVenue && (
        <Venue
          hasBusinessUnit={!!virtualVenue.businessUnitId}
          id={virtualVenue.id}
          isVirtual
          name="Offres numériques"
          offererId={selectedOffererId}
          hasMissingReimbursementPoint={
            virtualVenue.hasMissingReimbursementPoint
          }
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
          hasMissingReimbursementPoint={venue.hasMissingReimbursementPoint}
        />
      ))}
    </div>
  )
}
