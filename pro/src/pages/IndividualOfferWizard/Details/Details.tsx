import { useSelector } from 'react-redux'
import { useSearchParams } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GET_VENUES_QUERY_KEY } from 'config/swrQueryKeys'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { useCurrentUser } from 'hooks/useCurrentUser'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
import { DetailsScreen } from 'screens/IndividualOffer/DetailsScreen/DetailsScreen'
import { IndivualOfferLayout } from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { getTitle } from 'screens/IndividualOffer/IndivualOfferLayout/utils/getTitle'
import { selectCurrentOffererId } from 'store/user/selectors'
import { Spinner } from 'ui-kit/Spinner/Spinner'

const Details = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { currentUser } = useCurrentUser()
  const { offer } = useIndividualOfferContext()
  const [searchParams] = useSearchParams()

  const offererIdFromQueryParam = searchParams.get('structure')
    ? Number(searchParams.get('structure'))
    : undefined
  const selectedOffererId = useSelector(selectCurrentOffererId)

  // At first we look for the offerer id in the offer,
  // then in the query params
  // after all we look for the selected offerer id in the redux store
  const offererId =
    offer?.venue.managingOfferer.id ??
    offererIdFromQueryParam ??
    selectedOffererId

  const shouldNotFetchVenues = currentUser.isAdmin && !offererId

  const venuesQuery = useSWR(
    () => (shouldNotFetchVenues ? null : [GET_VENUES_QUERY_KEY, offererId]),
    ([, offererIdParam]) => api.getVenues(null, true, offererIdParam),
    { fallbackData: { venues: [] } }
  )

  if (venuesQuery.isLoading) {
    return <Spinner />
  }

  return (
    <IndivualOfferLayout offer={offer} title={getTitle(mode)} mode={mode}>
      <DetailsScreen venues={venuesQuery.data.venues} />
    </IndivualOfferLayout>
  )
}

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Details
