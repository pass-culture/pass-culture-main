import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'
import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'
import { useGetVenue } from 'core/Venue/adapters/getVenueAdapter'
import useNotification from 'hooks/useNotification'
import { getInterventionAreaLabels } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/EACInformation/utils/getInterventionAreaLabels'
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
    <SummaryLayout.SubSection title="Lieu de l'évènement">
      <SummaryLayout.Row
        description={formatOfferEventAddress(offer.offerVenue, venue)}
      />
      {interventionAreas && (
        <SummaryLayout.Row
          title="Zone de mobilité pour l'évènement"
          description={interventionAreas}
        />
      )}
    </SummaryLayout.SubSection>
  )
}
