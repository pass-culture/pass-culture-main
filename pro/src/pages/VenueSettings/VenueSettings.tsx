import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  GetVenueResponseModel,
  ListOffersOfferResponseModel,
  OfferStatus,
  ProviderResponse,
  VenueProviderResponse,
  VenueTypeResponseModel,
} from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { serializeApiFilters } from 'core/Offers/utils'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { serializeProvidersApi } from 'core/Venue/adapters/getProviderAdapter/serializers'
import { SelectOption } from 'custom_types/form'
import useNotification from 'hooks/useNotification'
import Spinner from 'ui-kit/Spinner/Spinner'
import { sortByLabel } from 'utils/strings'

import * as pcapi from '../../repository/pcapi/pcapi'

import { offerHasBookingQuantity } from './offerHasBookingQuantity'
import { setInitialFormValues } from './setInitialFormValues'
import { VenueSettingsFormScreen } from './VenueSettingsScreen'

const VenueSettings = (): JSX.Element | null => {
  const [isLoading, setIsLoading] = useState(false)
  const [venue, setVenue] = useState<GetVenueResponseModel>()
  const [venueTypes, setVenueTypes] = useState<SelectOption[]>()
  const [venueLabels, setVenueLabels] = useState<SelectOption[]>()
  const [offerer, setOfferer] = useState<GetOffererResponseModel>()
  const [providers, setProviders] = useState<ProviderResponse[]>()
  const [venueProviders, setVenueProviders] =
    useState<VenueProviderResponse[]>()
  const [venueOffers, setVenueOffers] = useState<{
    offers: ListOffersOfferResponseModel[]
  }>()

  const { offererId, venueId } = useParams<{
    offererId: string
    venueId: string
  }>()
  const notify = useNotification()
  const navigate = useNavigate()

  const apiFilters = {
    ...DEFAULT_SEARCH_FILTERS,
    status: OfferStatus.ACTIVE,
    venueId: venue?.id.toString() ?? '',
  }

  useEffect(() => {
    setIsLoading(true)

    async function getAllData() {
      try {
        const {
          nameOrIsbn,
          offererId,
          venueId,
          categoryId,
          status,
          creationMode,
          periodBeginningDate,
          periodEndingDate,
        } = serializeApiFilters(apiFilters)

        const [
          getVenue,
          getVenueTypes,
          getVenueLabels,
          getOfferer,
          getProviders,
          getListVenueProviders,
          getListOffers,
        ] = await Promise.all([
          api.getVenue(Number(venueId)),
          api.getVenueTypes(),
          api.fetchVenueLabels(),
          api.getOfferer(Number(offererId)),
          pcapi.loadProviders(Number(venueId)),
          api.listVenueProviders(Number(venueId)),
          api.listOffers(
            nameOrIsbn,
            offererId,
            status,
            venueId,
            categoryId,
            creationMode,
            periodBeginningDate,
            periodEndingDate
          ),
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

        setProviders(serializeProvidersApi(getProviders))

        setVenueProviders(getListVenueProviders.venue_providers)

        setVenueOffers({ offers: getListOffers })
      } catch (error) {
        navigate('/accueil')
        notify.error(GET_DATA_ERROR_MESSAGE)
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    getAllData()
    setIsLoading(false)
  }, [
    venueId,
    offererId,
    apiFilters.nameOrIsbn,
    apiFilters.offererId,
    apiFilters.venueId,
    apiFilters.categoryId,
    apiFilters.creationMode,
    apiFilters.periodBeginningDate,
    apiFilters.periodEndingDate,
  ])

  const hasBookingQuantity = offerHasBookingQuantity(venueOffers?.offers)

  if (isLoading) {
    return (
      <AppLayout>
        <Spinner />
      </AppLayout>
    )
  }

  if (!venue || !offerer || !venueLabels || !venueTypes) {
    return null
  }

  return (
    <AppLayout>
      <VenueSettingsFormScreen
        initialValues={setInitialFormValues(venue)}
        offerer={offerer}
        venueLabels={venueLabels}
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
