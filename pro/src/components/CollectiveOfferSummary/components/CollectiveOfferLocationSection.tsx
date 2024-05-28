import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import {
  Description,
  SummaryDescriptionList,
} from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { GET_VENUE_QUERY_KEY } from 'config/swrQueryKeys'
import { getInterventionAreaLabels } from 'pages/AdageIframe/app/components/OffersInstantSearch/OffersSearch/Offers/OfferDetails/OfferInterventionArea'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { formatOfferEventAddress } from './utils/formatOfferEventAddress'

interface CollectiveOfferLocationSectionProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
}

export const CollectiveOfferLocationSection = ({
  offer,
}: CollectiveOfferLocationSectionProps) => {
  const venueQuery = useSWR(
    [GET_VENUE_QUERY_KEY, offer.venue.id],
    ([, venueIdParam]) => api.getVenue(venueIdParam)
  )

  const interventionAreas = getInterventionAreaLabels(offer.interventionArea)

  const venue = venueQuery.data

  if (venueQuery.isLoading) {
    return <Spinner />
  }

  if (venueQuery.error) {
    return null
  }

  if (!venue) {
    return
  }

  const descriptions: Description[] = [
    { text: formatOfferEventAddress(offer.offerVenue, venue) },
  ]
  if (interventionAreas) {
    descriptions.push({
      title: 'Zone de mobilité pour l’évènement',
      text: interventionAreas,
    })
  }

  return (
    <SummarySubSection title="Lieu de l’évènement">
      <SummaryDescriptionList descriptions={descriptions} />
    </SummarySubSection>
  )
}
