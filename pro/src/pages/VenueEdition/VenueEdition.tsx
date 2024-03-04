import { useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'
import {
  generatePath,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
} from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  GetVenueResponseModel,
  VenueTypeResponseModel,
} from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import { SAVED_OFFERER_ID_KEY, GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'
import useNotification from 'hooks/useNotification'
import { CollectiveDataEdition } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition/CollectiveDataEdition'
import { updateSelectedOffererId } from 'store/user/reducer'
import Spinner from 'ui-kit/Spinner/Spinner'
import Tabs, { Tab } from 'ui-kit/Tabs/Tabs'
import { sortByLabel } from 'utils/strings'

import { setInitialFormValues } from './setInitialFormValues'
import { VenueEditionFormScreen } from './VenueEditionFormScreen'
import { VenueEditionHeader } from './VenueEditionHeader'

export const VenueEdition = (): JSX.Element | null => {
  const [isLoading, setIsLoading] = useState(false)
  const [venue, setVenue] = useState<GetVenueResponseModel>()
  const [venueTypes, setVenueTypes] = useState<SelectOption[]>()
  const [venueLabels, setVenueLabels] = useState<SelectOption[]>()
  const [offerer, setOfferer] = useState<GetOffererResponseModel>()

  const { offererId, venueId } = useParams<{
    offererId: string
    venueId: string
  }>()
  const notify = useNotification()
  const location = useLocation()
  const dispatch = useDispatch()
  const navigate = useNavigate()

  useEffect(() => {
    if (offererId) {
      localStorage.setItem(SAVED_OFFERER_ID_KEY, offererId)
      dispatch(updateSelectedOffererId(Number(offererId)))
    }
  }, [offererId, dispatch])

  useEffect(() => {
    setIsLoading(true)

    async function getAllData() {
      try {
        const [getVenue, getVenueTypes, getVenueLabels, getOfferer] =
          await Promise.all([
            api.getVenue(Number(venueId)),
            api.getVenueTypes(),
            api.fetchVenueLabels(),
            api.getOfferer(Number(offererId)),
          ])

        setVenue(getVenue)

        const wordToNotSort = getVenueTypes.filter(
          (type) => type.label === 'Autre'
        )
        const sortedTypes = sortByLabel(
          getVenueTypes.filter((type) => wordToNotSort.indexOf(type) === -1)
        ).concat(wordToNotSort)
        setVenueTypes(
          sortedTypes.map((type: VenueTypeResponseModel) => ({
            value: type.id,
            label: type.label,
          }))
        )

        setVenueLabels(
          getVenueLabels.map((type) => ({
            value: type.id.toString(),
            label: type.label,
          }))
        )

        setOfferer(getOfferer)
      } catch (error) {
        navigate('/accueil')
        notify.error(GET_DATA_ERROR_MESSAGE)
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    getAllData()
    setIsLoading(false)
  }, [venueId, offererId])

  if (isLoading) {
    return (
      <AppLayout>
        <Spinner />
      </AppLayout>
    )
  }

  if (!venue || !offerer || !venueTypes || !venueLabels) {
    return null
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
                venue={venue}
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
