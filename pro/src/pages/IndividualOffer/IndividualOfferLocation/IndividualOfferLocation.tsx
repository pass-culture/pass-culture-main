import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_VENUES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from '@/components/IndividualOfferLayout/utils/getTitle'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferLocationScreen } from './components/IndividualOfferLocationScreen'

export const IndividualOfferLocation = () => {
  const mode = useOfferWizardMode()
  const { offer } = useIndividualOfferContext()
  const venuesQuery = useSWR(
    offer ? [GET_VENUES_QUERY_KEY, offer.venue.managingOfferer.id] : null,
    ([, offererIdParam]) => api.getVenues(null, true, offererIdParam),
    { fallbackData: { venues: [] } }
  )

  // TODO (igabriele, 2025-08-20): Handle API error.s
  if (!offer || venuesQuery.isLoading) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout offer={offer} title={getTitle(mode)} mode={mode}>
      <IndividualOfferLocationScreen
        offer={offer}
        venues={venuesQuery.data.venues}
      />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferLocation
