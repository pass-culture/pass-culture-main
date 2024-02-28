import {
  generatePath,
  Navigate,
  Route,
  Routes,
  useLocation,
  useParams,
} from 'react-router-dom'

import { OfferStatus } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import { setInitialFormValues } from 'components/VenueForm'
import useGetOfferer from 'core/Offerers/getOffererAdapter/useGetOfferer'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { useGetVenue } from 'core/Venue/adapters/getVenueAdapter'
import { useGetVenueLabels } from 'core/Venue/adapters/getVenueLabelsAdapter'
import { useGetVenueTypes } from 'core/Venue/adapters/getVenueTypeAdapter'
import { useAdapter } from 'hooks'
import useNotification from 'hooks/useNotification'
import { CollectiveDataEdition } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition/CollectiveDataEdition'
import {
  getFilteredOffersAdapter,
  Payload,
} from 'pages/Offers/adapters/getFilteredOffersAdapter'
import { VenueEditionFormScreen } from 'screens/VenueForm/VenueEditionFormScreen'
import Spinner from 'ui-kit/Spinner/Spinner'
import Tabs, { Tab } from 'ui-kit/Tabs/Tabs'

import { offerHasBookingQuantity } from './utils'
import { VenueEditionHeader } from './VenueEditionHeader'

export const VenueEdition = (): JSX.Element | null => {
  const homePath = '/accueil'
  const { offererId, venueId } = useParams<{
    offererId: string
    venueId: string
  }>()
  const notify = useNotification()
  const location = useLocation()

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
    isLoading: isLoadingVenueLabels,
    error: errorVenueLabels,
    data: venueLabels,
  } = useGetVenueLabels()
  const {
    isLoading: isLoadingOfferer,
    error: errorOfferer,
    data: offerer,
  } = useGetOfferer(offererId)

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

  if (errorOfferer || errorVenue || errorVenueTypes || errorVenueLabels) {
    const loadingError = [
      errorOfferer,
      errorVenue,
      errorVenueTypes,
      errorVenueLabels,
    ].find((error) => error !== undefined)
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
    isLoadingVenueLabels ||
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

  const tabs: Tab[] = [
    {
      key: 'individual',
      label: 'Pour le grand public',
      url: generatePath('/structures/:offererId/lieux/:venueId', {
        offererId: String(offerer.id),
        venueId: String(venue.id),
      }),
    },
    {
      key: 'collective',
      label: 'Pour les enseignants',
      url: generatePath('/structures/:offererId/lieux/:venueId/eac', {
        offererId: String(offerer.id),
        venueId: String(venue.id),
      }),
    },
  ]
  const activeStep = location.pathname.includes('eac')
    ? 'collective'
    : 'individual'

  return (
    <AppLayout layout={'sticky-actions'}>
      <div>
        <VenueEditionHeader
          venue={venue}
          offerer={offerer}
          venueTypes={venueTypes}
        />

        <Tabs tabs={tabs} selectedKey={activeStep} />

        <Routes>
          <Route
            path=""
            element={
              <VenueEditionFormScreen
                initialValues={setInitialFormValues(venue)}
                offerer={offerer}
                venueTypes={venueTypes}
                venueLabels={venueLabels}
                venue={venue}
                hasBookingQuantity={venue?.id ? hasBookingQuantity : false}
              />
            }
          />
          <Route path="eac" element={<CollectiveDataEdition venue={venue} />} />
        </Routes>
      </div>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = VenueEdition
