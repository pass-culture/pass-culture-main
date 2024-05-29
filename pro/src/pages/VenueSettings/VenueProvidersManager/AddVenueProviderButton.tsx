import React, { useState } from 'react'
import useSWR, { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { GetVenueResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import {
  GET_PROVIDERS_QUERY_KEY,
  GET_VENUE_PROVIDERS_QUERY_KEY,
} from 'config/swrQueryKeys'
import { SynchronizationEvents } from 'core/FirebaseEvents/constants'
import fullMoreIcon from 'icons/full-more.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { sortByLabel } from 'utils/strings'

import { DEFAULT_PROVIDER_OPTION } from './utils/_constants'
import { VenueProviderForm } from './VenueProviderForm'

interface AddVenueProviderButtonProps {
  venue: GetVenueResponseModel
}

export const AddVenueProviderButton = ({
  venue,
}: AddVenueProviderButtonProps) => {
  const { mutate } = useSWRConfig()

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

  const providersOptions = sortByLabel(
    providers.map((item) => ({
      value: item['id'].toString(),
      label: item['name'],
    }))
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
    cancelProviderSelection()
    await mutate([GET_VENUE_PROVIDERS_QUERY_KEY, venue.id])
  }

  const AddButton = (
    <Button
      onClick={setCreationMode}
      variant={ButtonVariant.SECONDARY}
      icon={fullMoreIcon}
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
          placeholder="Choix du logiciel"
        />
      </FieldLayout>

      {selectedProvider && (
        <VenueProviderForm
          afterSubmit={afterSubmit}
          provider={selectedProvider}
          venue={venue}
        />
      )}
    </>
  )

  return isCreationMode ? VenueProviderSelection : AddButton
}
