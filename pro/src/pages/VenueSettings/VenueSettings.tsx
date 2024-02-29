import { Navigate, useParams } from 'react-router-dom'

import { OfferStatus } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import useGetOfferer from 'core/Offerers/getOffererAdapter/useGetOfferer'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { useGetVenue } from 'core/Venue/adapters/getVenueAdapter'
import { useGetVenueTypes } from 'core/Venue/adapters/getVenueTypeAdapter'
import { useAdapter } from 'hooks'
import useNotification from 'hooks/useNotification'
import {
  getFilteredOffersAdapter,
  Payload,
} from 'pages/Offers/adapters/getFilteredOffersAdapter'
import Spinner from 'ui-kit/Spinner/Spinner'

import useGetProviders from '../../core/Venue/adapters/getProviderAdapter/useGetProvider'
import useGetVenueProviders from '../../core/Venue/adapters/getVenueProviderAdapter/useGetVenueProvider'

import { offerHasBookingQuantity } from './offerHasBookingQuantity'
import { setInitialFormValues } from './setInitialFormValues'
import { VenueSettingsFormScreen } from './VenueSettingsScreen'

const VenueSettings = (): JSX.Element | null => {
  const homePath = '/accueil'
  const { offererId, venueId } = useParams<{
    offererId: string
    venueId: string
  }>()
  const notify = useNotification()

  // TODO: refactor with the new loading pattern once we know which one to use
  const {
    isLoading: isLoadingVenue,
    error: errorVenue,
    data: venue,
  } = useGetVenue(Number(venueId))
  const {
    isLoading: isLoadingVenueTypes,
    error: errorVenueTypes,
    data: venueTypes,
  } = useGetVenueTypes()
  const {
    isLoading: isLoadingOfferer,
    error: errorOfferer,
    data: offerer,
  } = useGetOfferer(offererId)
  const {
    isLoading: isLoadingProviders,
    error: errorProviders,
    data: providers,
  } = useGetProviders(Number(venueId))
  const {
    isLoading: isLoadingVenueProviders,
    error: errorVenueProviders,
    data: venueProviders,
  } = useGetVenueProviders(Number(venueId))

  const apiFilters = {
    ...DEFAULT_SEARCH_FILTERS,
    status: OfferStatus.ACTIVE,
    venueId: venue?.id.toString() ?? '',
  }

  const { isLoading: isLoadingVenueOffers, data: venueOffers } = useAdapter<
    Payload,
    Payload
  >(() => getFilteredOffersAdapter(apiFilters))

  const hasBookingQuantity = offerHasBookingQuantity(venueOffers?.offers)

  if (
    errorOfferer ||
    errorVenue ||
    errorVenueTypes ||
    errorVenueProviders ||
    errorProviders
  ) {
    const loadingError = [errorOfferer, errorVenue, errorVenueTypes].find(
      (error) => error !== undefined
    )
    if (loadingError !== undefined) {
      notify.error(loadingError.message)
      return <Navigate to={homePath} />
    }
    /* istanbul ignore next: Never */
    return null
  }

  if (
    isLoadingVenue ||
    isLoadingVenueTypes ||
    isLoadingProviders ||
    isLoadingVenueProviders ||
    isLoadingOfferer ||
    isLoadingVenueOffers ||
    !offerer ||
    !venue
  ) {
    return (
      <AppLayout>
        <Spinner />
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <VenueSettingsFormScreen
        initialValues={setInitialFormValues(venue)}
        offerer={offerer}
        venueTypes={venueTypes}
        providers={providers}
        venue={venue}
        venueProviders={venueProviders}
        hasBookingQuantity={venue?.id ? hasBookingQuantity : false}
      />
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = VenueSettings
