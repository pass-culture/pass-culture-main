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

import { AppLayout } from 'app/AppLayout'
import useGetOfferer from 'core/Offerers/getOffererAdapter/useGetOfferer'
import { SAVED_OFFERER_ID_KEY } from 'core/shared'
import { useGetVenue } from 'core/Venue/adapters/getVenueAdapter'
import { useGetVenueTypes } from 'core/Venue/adapters/getVenueTypeAdapter'
import useNotification from 'hooks/useNotification'
import { CollectiveDataEdition } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition/CollectiveDataEdition'
import { CollectiveDataEditionReadOnly } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition/CollectiveDataEditionReadOnly'
import { updateSelectedOffererId } from 'store/user/reducer'
import Spinner from 'ui-kit/Spinner/Spinner'
import Tabs, { Tab } from 'ui-kit/Tabs/Tabs'

import { setInitialFormValues } from './setInitialFormValues'
import styles from './VenueEdition.module.scss'
import { VenueEditionFormScreen } from './VenueEditionFormScreen'
import { VenueEditionHeader } from './VenueEditionHeader'
import { VenueEditionReadOnly } from './VenueEditionReadOnly'

export const VenueEdition = (): JSX.Element | null => {
  const homePath = '/accueil'
  const { offererId, venueId } = useParams<{
    offererId: string
    venueId: string
  }>()
  const notify = useNotification()
  const location = useLocation()
  const dispatch = useDispatch()

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

  useEffect(() => {
    if (offererId) {
      localStorage.setItem(SAVED_OFFERER_ID_KEY, offererId)
      dispatch(updateSelectedOffererId(Number(offererId)))
    }
  }, [offererId, dispatch])

  if (errorOfferer || errorVenue || errorVenueTypes) {
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
    isLoadingOfferer ||
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
          <Route path="" element={<VenueEditionReadOnly venue={venue} />} />
          <Route
            path="/edition"
            element={
              <VenueEditionFormScreen
                initialValues={setInitialFormValues(venue)}
                venue={venue}
              />
            }
          />
          <Route
            path="eac"
            element={<CollectiveDataEditionReadOnly venue={venue} />}
          />
          <Route
            path="eac/edition"
            element={<CollectiveDataEdition venue={venue} />}
          />
        </Routes>
      </div>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = VenueEdition
