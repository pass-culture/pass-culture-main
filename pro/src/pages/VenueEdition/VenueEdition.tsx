import { useEffect } from 'react'
import { useDispatch } from 'react-redux'
import {
  generatePath,
  Navigate,
  Route,
  Routes,
  useLocation,
  useParams,
} from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { AppLayout } from 'app/AppLayout'
import useGetOfferer from 'core/Offerers/getOffererAdapter/useGetOfferer'
import { SAVED_OFFERER_ID_KEY } from 'core/shared'
import { useGetVenueTypes } from 'core/Venue/adapters/getVenueTypeAdapter'
import useNotification from 'hooks/useNotification'
import { CollectiveDataEdition } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition/CollectiveDataEdition'
import { updateSelectedOffererId } from 'store/user/reducer'
import Spinner from 'ui-kit/Spinner/Spinner'
import Tabs, { Tab } from 'ui-kit/Tabs/Tabs'

import styles from './VenueEdition.module.scss'
import { VenueEditionFormScreen } from './VenueEditionFormScreen'
import { VenueEditionHeader } from './VenueEditionHeader'

export const GET_VENUE_QUERY_KEY = 'getVenue'

export const VenueEdition = (): JSX.Element | null => {
  const homePath = '/accueil'
  const { offererId, venueId } = useParams<{
    offererId: string
    venueId: string
  }>()
  const notify = useNotification()
  const location = useLocation()
  const dispatch = useDispatch()

  const venueQuery = useSWR(
    [GET_VENUE_QUERY_KEY, venueId],
    ([, venueIdParam]) => api.getVenue(Number(venueIdParam))
  )

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

  useEffect(() => {
    if (offererId) {
      localStorage.setItem(SAVED_OFFERER_ID_KEY, offererId)
      dispatch(updateSelectedOffererId(Number(offererId)))
    }
  }, [offererId, dispatch])

  if (errorOfferer || venueQuery.error || errorVenueTypes) {
    const loadingError = [errorOfferer, venueQuery.error, errorVenueTypes].find(
      (error) => error !== undefined
    )
    if (loadingError !== undefined) {
      notify.error(
        'Une erreur est survenue lors de la récupération de votre lieu'
      )
      return <Navigate to={homePath} />
    }
    /* istanbul ignore next: Never */
    return null
  }

  const venue = venueQuery.data

  if (
    venueQuery.isLoading ||
    isLoadingVenueTypes ||
    isLoadingOfferer ||
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
        offererId: String(venue.managingOfferer.id),
        venueId: String(venue.id),
      }),
    },
    {
      key: 'collective',
      label: 'Pour les enseignants',
      url: generatePath('/structures/:offererId/lieux/:venueId/eac', {
        offererId: String(venue.managingOfferer.id),
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

        <Tabs tabs={tabs} selectedKey={activeStep} className={styles['tabs']} />

        <Routes>
          <Route
            path="eac/*"
            element={<CollectiveDataEdition venue={venue} />}
          />
          <Route path="*" element={<VenueEditionFormScreen venue={venue} />} />
        </Routes>
      </div>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = VenueEdition
