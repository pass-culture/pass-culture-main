import { useRef, useState } from 'react'
import useSWR, { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { GetVenueResponseModel, ProviderResponse } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import {
  GET_PROVIDERS_QUERY_KEY,
  GET_VENUE_PROVIDERS_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { SynchronizationEvents } from 'commons/core/FirebaseEvents/constants'
import { sortByLabel } from 'commons/utils/strings'
import fullMoreIcon from 'icons/full-more.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { DEFAULT_PROVIDER_OPTION } from './utils/_constants'
import { VenueProviderForm } from './VenueProviderForm'

export interface AddVenueProviderButtonProps {
  venue: GetVenueResponseModel
  linkedProviders: ProviderResponse[]
}

export const AddVenueProviderButton = ({
  venue,
  linkedProviders,
}: AddVenueProviderButtonProps) => {
  const { mutate } = useSWRConfig()

  const providerSelectRef = useRef<HTMLSelectElement>(null)
  const selectSoftwareButtonRef = useRef<HTMLButtonElement>(null)

  const providersQuery = useSWR(
    [GET_PROVIDERS_QUERY_KEY, venue.id],
    ([, venueIdParam]) => api.getProvidersByVenue(venueIdParam)
  )
  const providers = providersQuery.data

  const { logEvent } = useAnalytics()
  const [isCreationMode, setIsCreationMode] = useState(false)
  const [selectedProviderId, setSelectedProviderId] = useState(
    DEFAULT_PROVIDER_OPTION.value
  )

  if (providersQuery.isLoading || !providers) {
    return <Spinner />
  }

  const selectedProvider = providers.find(
    (provider) => provider.id.toString() === selectedProviderId
  )

  const venueIsLinkedToIntegratedProvider = linkedProviders.find(
    (provider) => !provider.hasOffererProvider
  )

  const providersOptions = sortByLabel(
    // 1. Filter out providers that are already linked to the venue
    //    And if the venue is already linked to an integrated provider,
    //    filter out other integrated providers
    // 2. Format providers
    providers.reduce(
      (
        filteredProvidersOptions: { value: string; label: string }[],
        provider
      ) => {
        const shouldBeFilteredOut = !!linkedProviders.find(
          (linkedProvider) =>
            // venue already linked to this provider
            provider.id === linkedProvider.id ||
            // venue already linked to an integrated provider
            (venueIsLinkedToIntegratedProvider && !provider.hasOffererProvider)
        )

        if (!shouldBeFilteredOut) {
          return [
            ...filteredProvidersOptions,
            {
              value: provider['id'].toString(),
              label: provider['name'],
            },
          ]
        }

        return filteredProvidersOptions
      },
      []
    )
  )

  const setCreationMode = () => {
    logEvent(SynchronizationEvents.CLICKED_SYNCHRONIZE_OFFER, {
      offererId: venue.managingOfferer.id,
      venueId: venue.id,
    })
    setIsCreationMode(true)
  }

  const cancelProviderSelection = () => {
    setIsCreationMode(false)
    setSelectedProviderId(DEFAULT_PROVIDER_OPTION.value)
  }

  const afterSubmit = async () => {
    selectSoftwareButtonRef.current?.focus()
    cancelProviderSelection()
    await mutate([GET_VENUE_PROVIDERS_QUERY_KEY, venue.id])
  }

  const AddButton = (
    <Button
      onClick={setCreationMode}
      variant={ButtonVariant.SECONDARY}
      icon={fullMoreIcon}
      ref={selectSoftwareButtonRef}
    >
      Sélectionner un logiciel
    </Button>
  )

  const VenueProviderSelection = (
    <>
      <FieldLayout label="Logiciel" name="provider">
        <SelectInput
          defaultOption={DEFAULT_PROVIDER_OPTION}
          onChange={(event) => setSelectedProviderId(event.target.value)}
          name="provider"
          options={providersOptions}
          value={String(selectedProviderId)}
          data-testid="provider-select"
          ref={providerSelectRef}
        />
      </FieldLayout>

      {selectedProvider && (
        <VenueProviderForm
          afterSubmit={afterSubmit}
          provider={selectedProvider}
          venue={venue}
          providerSelectRef={providerSelectRef}
        />
      )}
    </>
  )

  return isCreationMode ? VenueProviderSelection : AddButton
}
