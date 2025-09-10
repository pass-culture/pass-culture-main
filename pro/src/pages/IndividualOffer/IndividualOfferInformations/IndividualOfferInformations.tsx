import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_VENUES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferLocation } from '../IndividualOfferLocation/IndividualOfferLocation'
import { IndividualOfferInformationsScreen } from './components/IndividualOfferInformationsScreen'

// TODO (igabriele, 2025-08-14): Replace this page with `<IndividualOfferLocation />` once `WIP_ENABLE_NEW_OFFER_CREATION_FLOW` FF is enabled in production.
const IndividualOfferInformations = (): JSX.Element | null => {
  const { offer } = useIndividualOfferContext()
  const isNewOfferCreationFlowFeatureActive = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )

  // Getting selected venue at step 1 (details) to infer address fields
  const venuesQuery = useSWR(
    offer ? [GET_VENUES_QUERY_KEY, offer.venue.managingOfferer.id] : null,
    ([, offererIdParam]) => api.getVenues(null, true, offererIdParam),
    { fallbackData: { venues: [] } }
  )

  if (isNewOfferCreationFlowFeatureActive) {
    return <IndividualOfferLocation />
  }

  const selectedVenue = venuesQuery.data.venues.find(
    (v) => v.id.toString() === offer?.venue.id.toString()
  )

  if (!offer || venuesQuery.isLoading) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout offer={offer}>
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
