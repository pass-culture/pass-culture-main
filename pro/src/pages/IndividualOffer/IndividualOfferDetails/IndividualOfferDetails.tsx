import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_VENUES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferDetailsScreen } from './components/IndividualOfferDetailsScreen'

// TODO (igabriele, 2026-01-05): Rename to `IndividualOfferDescription`.
const IndividualOfferDetails = (): JSX.Element | null => {
  const { offer } = useIndividualOfferContext()

  const selectedOffererId = useAppSelector(selectCurrentOffererId)

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
    <IndividualOfferLayout offer={offer}>
      <IndividualOfferDetailsScreen venues={venuesQuery.data.venues} />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferDetails
