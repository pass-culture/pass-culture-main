import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'
import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'
import { useGetVenue } from 'core/Venue'
import useNotification from 'hooks/useNotification'
import Spinner from 'ui-kit/Spinner/Spinner'

import { DEFAULT_RECAP_VALUE } from '../constants'
import { formatOfferEventAddress } from '../utils/formatOfferEventAddress'

interface ICollectiveOfferPracticalInformationSectionProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
}

const CollectiveOfferPracticalInformationSection = ({
  offer,
}: ICollectiveOfferPracticalInformationSectionProps) => {
  const notify = useNotification()
  const {
    error,
    isLoading,
    data: venue,
  } = useGetVenue(offer.venue.nonHumanizedId)
  if (isLoading) {
    return <Spinner />
  }
  if (error) {
    notify.error(error.message)
    return null
  }

  return (
    <SummaryLayout.SubSection title="Informations pratiques">
      <SummaryLayout.Row
        title="Adresse où se déroulera l’évènement"
        description={formatOfferEventAddress(offer.offerVenue, venue)}
      />
      {offer.isTemplate && (
        <SummaryLayout.Row
          title="Informations sur le prix"
          description={offer.educationalPriceDetail || DEFAULT_RECAP_VALUE}
        />
      )}
    </SummaryLayout.SubSection>
  )
}

export default CollectiveOfferPracticalInformationSection
