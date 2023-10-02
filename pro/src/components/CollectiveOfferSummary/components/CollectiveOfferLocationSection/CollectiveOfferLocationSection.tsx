import React from 'react'

import { SummaryRow } from 'components/SummaryLayout/SummaryRow'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'
import { useGetVenue } from 'core/Venue/adapters/getVenueAdapter'
import useNotification from 'hooks/useNotification'
import { getInterventionAreaLabels } from 'pages/AdageIframe/app/components/OffersInstantSearch/OffersSearch/Offers/OfferDetails/OfferInterventionArea/OfferInterventionArea'
import Spinner from 'ui-kit/Spinner/Spinner'

import { formatOfferEventAddress } from '../utils/formatOfferEventAddress'

interface CollectiveOfferLocationSectionProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
}

export default function CollectiveOfferLocationSection({
  offer,
}: CollectiveOfferLocationSectionProps) {
  const notify = useNotification()
  const { error, isLoading, data: venue } = useGetVenue(offer.venue.id)

  const interventionAreas = getInterventionAreaLabels(offer.interventionArea)

  if (isLoading) {
    return <Spinner />
  }
  if (error) {
    notify.error(error.message)
    return null
  }

  return (
    <SummarySubSection title="Lieu de l’évènement">
      <SummaryRow
        description={formatOfferEventAddress(offer.offerVenue, venue)}
      />
      {interventionAreas && (
        <SummaryRow
          title="Zone de mobilité pour l’évènement"
          description={interventionAreas}
        />
      )}
    </SummarySubSection>
  )
}
