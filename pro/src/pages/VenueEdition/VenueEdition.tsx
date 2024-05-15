import { useEffect } from 'react'
import { useDispatch } from 'react-redux'
import {
  generatePath,
  Route,
  Routes,
  useLocation,
  useParams,
} from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { AppLayout } from 'app/AppLayout'
import {
  GET_OFFERER_QUERY_KEY,
  GET_VENUE_QUERY_KEY,
  GET_VENUE_TYPES_QUERY_KEY,
} from 'config/swrQueryKeys'
import { SAVED_OFFERER_ID_KEY } from 'core/shared/constants'
import { CollectiveDataEdition } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition/CollectiveDataEdition'
import { updateSelectedOffererId } from 'store/user/reducer'
import Spinner from 'ui-kit/Spinner/Spinner'
import { Tab, Tabs } from 'ui-kit/Tabs/Tabs'

import styles from './VenueEdition.module.scss'
import { VenueEditionFormScreen } from './VenueEditionFormScreen'
import { VenueEditionHeader } from './VenueEditionHeader'

export const VenueEdition = (): JSX.Element | null => {
  const { offererId, venueId } = useParams<{
    offererId: string
    venueId: string
  }>()
  const location = useLocation()
  const dispatch = useDispatch()

  const venueQuery = useSWR(
    [GET_VENUE_QUERY_KEY, venueId],
    ([, venueIdParam]) => api.getVenue(Number(venueIdParam))
  )
  const venue = venueQuery.data

  const offererQuery = useSWR(
    [GET_OFFERER_QUERY_KEY, offererId],
    ([, offererIdParam]) => api.getOfferer(Number(offererIdParam))
  )
  const offerer = offererQuery.data

  const venueTypesQuery = useSWR([GET_VENUE_TYPES_QUERY_KEY], () =>
    api.getVenueTypes()
  )
  const venueTypes = venueTypesQuery.data

  useEffect(() => {
    if (offererId) {
      localStorage.setItem(SAVED_OFFERER_ID_KEY, offererId)
      dispatch(updateSelectedOffererId(Number(offererId)))
    }
  }, [offererId, dispatch])

  if (
    venueQuery.isLoading ||
    venueTypesQuery.isLoading ||
    offererQuery.isLoading ||
    !venue ||
    !offerer ||
    !venueTypes
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
      url: generatePath('/structures/:offererId/lieux/:venueId/collectif', {
        offererId: String(venue.managingOfferer.id),
        venueId: String(venue.id),
      }),
    },
  ]
  const activeStep = location.pathname.includes('collectif')
    ? 'collective'
    : 'individual'

  return (
    <AppLayout>
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
