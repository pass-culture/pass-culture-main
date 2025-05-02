import { useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GET_VENUES_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { IndividualOfferLayout } from 'components/IndividualOffer/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from 'components/IndividualOffer/IndividualOfferLayout/utils/getTitle'
import { IndividualOfferDetailsScreen } from 'pages/IndividualOffer/IndividualOfferDetails/components/IndividualOfferDetailsScreen'
import { Spinner } from 'ui-kit/Spinner/Spinner'

const IndividualOfferDetails = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer, publishedOfferWithSameEAN } = useIndividualOfferContext()

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
      <IndividualOfferDetailsScreen venues={venuesQuery.data.venues} />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferDetails
