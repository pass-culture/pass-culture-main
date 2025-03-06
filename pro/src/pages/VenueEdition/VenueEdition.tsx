import { useEffect } from 'react'
import { useSelector } from 'react-redux'
import {
  generatePath,
  useLocation,
  useNavigate,
  useParams,
} from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { Layout } from 'app/App/layout/Layout'
import {
  GET_VENUE_QUERY_KEY,
  GET_VENUE_TYPES_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { SelectOption } from 'commons/custom_types/form'
import { useOfferer } from 'commons/hooks/swr/useOfferer'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
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
  const location = useLocation()
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const venueQuery = useSWR(
    [GET_VENUE_QUERY_KEY, venueId],
    ([, venueIdParam]) => api.getVenue(Number(venueIdParam))
  )
  const venue = venueQuery.data

  const { data: offerer, isLoading: isOffererLoading } = useOfferer(offererId)

  const venueTypesQuery = useSWR([GET_VENUE_TYPES_QUERY_KEY], () =>
    api.getVenueTypes()
  )
  const venueTypes = venueTypesQuery.data

  useEffect(() => {
    if (selectedOffererId?.toString() !== offererId) {
      navigate('/accueil')
    }
  }, [selectedOffererId, offererId])

  if (
    venueQuery.isLoading ||
    venueTypesQuery.isLoading ||
    isOffererLoading ||
    !venue ||
    !offerer ||
    !venueTypes
  ) {
    return (
      <Layout>
        <Spinner />
      </Layout>
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
    <Layout mainHeading={titleText}>
      <div>
        <FormLayout>
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
                    value={venueId ?? ''}
                    onChange={(e) => {
                      navigate(
                        `/structures/${offererId}/lieux/${e.target.value}`
                      )
                    }}
                  />
                </FieldLayout>
              </FormLayout.Row>
              <hr className={styles['separator']} />
            </>
          )}
        </FormLayout>
        <VenueEditionHeader
          venue={venue}
          offerer={offerer}
          venueTypes={venueTypes}
          key={venueId}
        />

        {!venue.isPermanent && (
          <Tabs
            tabs={tabs}
            selectedKey={activeStep}
            className={styles['tabs']}
          />
        )}

        {activeStep === 'collective' && <CollectiveDataEdition venue={venue} />}
        {activeStep === 'individual' && (
          <VenueEditionFormScreen venue={venue} />
        )}
      </div>
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = VenueEdition
