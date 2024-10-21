import { useState } from 'react'
import { useSelector } from 'react-redux'
import {
  generatePath,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
} from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { AppLayout } from 'app/AppLayout'
import {
  GET_OFFERER_QUERY_KEY,
  GET_VENUE_QUERY_KEY,
  GET_VENUE_TYPES_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { SelectOption } from 'commons/custom_types/form'
import { useIsNewInterfaceActive } from 'commons/hooks/useIsNewInterfaceActive'
import { selectCurrentOffererId } from 'commons/store/user/selectors'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { CollectiveDataEdition } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition/CollectiveDataEdition'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { Tab, Tabs } from 'ui-kit/Tabs/Tabs'

import styles from './VenueEdition.module.scss'
import { VenueEditionFormScreen } from './VenueEditionFormScreen'
import { VenueEditionHeader } from './VenueEditionHeader'

export const VenueEdition = (): JSX.Element | null => {
  const { offererId, venueId } = useParams<{
    offererId: string
    venueId: string
  }>()
  const navigate = useNavigate()
  const [selectedVenueId, setSelectedVenueId] = useState(venueId ?? '')
  const location = useLocation()
  const isNewSideBarNavigation = useIsNewInterfaceActive()
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const venueQuery = useSWR(
    [GET_VENUE_QUERY_KEY, selectedVenueId || venueId],
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

  if (selectedOffererId?.toString() !== offererId) {
    navigate('/accueil')
    return null
  }

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

  const permanentVenues =
    offerer.managedVenues?.filter((venue) => venue.isPermanent) ?? []

  const venuesOptions: SelectOption[] = permanentVenues.map((venue) => ({
    label: venue.publicName || venue.name,
    value: venue.id.toString(),
  }))

  const titleText =
    activeStep === 'collective'
      ? 'Page dans ADAGE'
      : !venue.isPermanent
        ? 'Page adresse'
        : 'Page sur l’application'

  return (
    <AppLayout>
      <div>
        {isNewSideBarNavigation && (
          <FormLayout>
            <h1 className={styles['header']}>{titleText}</h1>
            {venuesOptions.length > 1 && venue.isPermanent && (
              <>
                <FormLayout.Row>
                  <FieldLayout
                    label={`Sélectionnez votre page ${activeStep === 'individual' ? 'partenaire' : 'dans ADAGE'}`}
                    name="venues"
                    isOptional
                    className={styles['select-partner-page']}
                  >
                    <SelectInput
                      name="venues"
                      options={venuesOptions}
                      value={selectedVenueId}
                      onChange={(e) => {
                        setSelectedVenueId(e.target.value)
                      }}
                    />
                  </FieldLayout>
                </FormLayout.Row>
                <hr className={styles['separator']} />
              </>
            )}
          </FormLayout>
        )}
        <VenueEditionHeader
          venue={venue}
          offerer={offerer}
          venueTypes={venueTypes}
        />

        {(!isNewSideBarNavigation || !venue.isPermanent) && (
          <Tabs
            tabs={tabs}
            selectedKey={activeStep}
            className={styles['tabs']}
          />
        )}

        <Routes>
          <Route
            path="collectif/*"
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
