import { useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from '@/apiClient//api'
import { GET_VENUES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from '@/components/IndividualOfferLayout/utils/getTitle'
import { IndividualOfferDetailsScreen } from '@/pages/IndividualOffer/IndividualOfferDetails/components/IndividualOfferDetailsScreen'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferDetailsScreenNext } from './components/IndividualOfferDetailsScreenNext'

const IndividualOfferDetails = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer, publishedOfferWithSameEAN } = useIndividualOfferContext()
  const isNewOfferCreationFlowFeatureActive = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )

  const selectedOffererId = useSelector(selectCurrentOffererId)

  // At first we look for the offerer id in the offer,
  // else we look for the selected offerer id in the redux store
  const offererId = offer?.venue.managingOfferer.id ?? selectedOffererId

  const venuesQuery = useSWR(
    () => [GET_VENUES_QUERY_KEY, offererId],
    ([, offererIdParam]) => api.getVenues(null, true, offererIdParam),
    { fallbackData: { venues: [] } }
  )

  if (venuesQuery.isLoading) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout
      offer={offer}
      title={getTitle(mode)}
      mode={mode}
      venueHasPublishedOfferWithSameEan={Boolean(publishedOfferWithSameEAN)}
    >
      {isNewOfferCreationFlowFeatureActive ? (
        <IndividualOfferDetailsScreenNext venues={venuesQuery.data.venues} />
      ) : (
        <IndividualOfferDetailsScreen venues={venuesQuery.data.venues} />
      )}
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferDetails
