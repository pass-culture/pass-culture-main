import { useParams, useNavigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { Layout } from 'app/App/layout/Layout'
import {
  GET_VENUE_PROVIDERS_QUERY_KEY,
  GET_VENUE_QUERY_KEY,
  GET_VENUE_TYPES_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { useOfferer } from 'commons/hooks/swr/useOfferer'
import fullBackIcon from 'icons/full-back.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { setInitialFormValues } from './setInitialFormValues'
import { VenueSettingsScreen } from './VenueSettingsScreen'

const VenueSettings = (): JSX.Element | null => {
  const navigate = useNavigate()

  const { offererId, venueId } = useParams<{
    offererId: string
    venueId: string
  }>()

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

  const venueProvidersQuery = useSWR(
    [GET_VENUE_PROVIDERS_QUERY_KEY, Number(venueId)],
    ([, venueIdParam]) => api.listVenueProviders(venueIdParam)
  )
  const venueProviders = venueProvidersQuery.data?.venue_providers

  if (
    isOffererLoading ||
    venueQuery.isLoading ||
    venueTypesQuery.isLoading ||
    venueProvidersQuery.isLoading ||
    !offerer ||
    !venue ||
    !venueTypes ||
    !venueProviders
  ) {
    return (
      <Layout>
        <Spinner />
      </Layout>
    )
  }

  return (
    <Layout
      mainHeading="Paramètres généraux"
      mainTopElement={
        <Button
          variant={ButtonVariant.TERNARYPINK}
          icon={fullBackIcon}
          onClick={() => navigate(-1)}
        >
          Retour vers la page précédente
        </Button>
      }
    >
      <VenueSettingsScreen
        initialValues={setInitialFormValues({ venue })}
        offerer={offerer}
        venueTypes={venueTypes}
        venue={venue}
        venueProviders={venueProviders}
      />
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = VenueSettings
