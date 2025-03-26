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

import { getPathToNavigateTo } from './context'
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

  const isPageLoading =
    venueQuery.isLoading ||
    venueTypesQuery.isLoading ||
    isOffererLoading ||
    !venue ||
    !offerer ||
    !venueTypes

  const tabs: Tab[] = [
    {
      key: 'individual',
      label: 'Pour le grand public',
      url: generatePath('/structures/:offererId/lieux/:venueId', {
        offererId: String(venue?.managingOfferer.id),
        venueId: String(venue?.id),
      }),
    },
    {
      key: 'collective',
      label: 'Pour les enseignants',
      url: generatePath('/structures/:offererId/lieux/:venueId/collectif', {
        offererId: String(venue?.managingOfferer.id),
        venueId: String(venue?.id),
      }),
    },
  ]

  const context = location.pathname.includes('collectif')
    ? 'collective'
    : location.pathname.includes('page-partenaire')
      ? 'partnerPage'
      : 'address'

  const filteredVenues =
    offerer?.managedVenues?.filter((venue) =>
      context === 'partnerPage' ? venue.hasPartnerPage : venue.isPermanent
    ) ?? []

  const venuesOptions: SelectOption[] = filteredVenues.map((venue) => ({
    label: venue.publicName || venue.name,
    value: venue.id.toString(),
  }))

  const titleText =
    context === 'collective'
      ? 'Page dans ADAGE'
      : context === 'partnerPage'
        ? 'Page sur l’application'
        : 'Page adresse'

  return (
    <Layout mainHeading={titleText}>
      {isPageLoading ? (
        <Spinner />
      ) : (
        <div>
          <FormLayout>
            {context !== 'address' && venuesOptions.length > 1 && (
              <>
                <FormLayout.Row>
                  <FieldLayout
                    label={`Sélectionnez votre page ${context === 'collective' ? 'dans ADAGE' : 'partenaire'}`}
                    name="venues"
                    isOptional
                    className={styles['select-page-partenaire']}
                  >
                    <SelectInput
                      name="venues"
                      options={venuesOptions}
                      value={venueId ?? ''}
                      onChange={(e) => {
                        const venueId = e.target.value
                        const path = getPathToNavigateTo(
                          offererId as string,
                          venueId
                        )
                        navigate(path)
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
              selectedKey={
                context === 'collective' ? 'collective' : 'individual'
              }
              className={styles['tabs']}
            />
          )}

          {context === 'collective' ? (
            <CollectiveDataEdition venue={venue} />
          ) : (
            <VenueEditionFormScreen venue={venue} />
          )}
        </div>
      )}
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = VenueEdition
