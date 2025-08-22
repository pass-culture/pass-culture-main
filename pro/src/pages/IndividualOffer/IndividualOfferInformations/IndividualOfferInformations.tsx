import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_VENUES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from '@/components/IndividualOfferLayout/utils/getTitle'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferInformationsScreen } from './components/IndividualOfferInformationsScreen'

const IndividualOfferInformations = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer, publishedOfferWithSameEAN } = useIndividualOfferContext()

  // Getting selected venue at step 1 (details) to infer address fields
  const venuesQuery = useSWR(
    offer ? [GET_VENUES_QUERY_KEY, offer.venue.managingOfferer.id] : null,
    ([, offererIdParam]) => api.getVenues(null, true, offererIdParam),
    { fallbackData: { venues: [] } }
  )

  const selectedVenue = venuesQuery.data.venues.find(
    (v) => v.id.toString() === offer?.venue.id.toString()
  )

  if (!offer || venuesQuery.isLoading) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout
      offer={offer}
      title={getTitle(mode)}
      mode={mode}
      venueHasPublishedOfferWithSameEan={Boolean(publishedOfferWithSameEAN)}
    >
      <IndividualOfferInformationsScreen
        offer={offer}
        selectedVenue={selectedVenue}
      />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferInformations
