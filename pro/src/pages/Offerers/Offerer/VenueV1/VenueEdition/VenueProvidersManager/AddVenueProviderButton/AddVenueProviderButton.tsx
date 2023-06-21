import './AddVenueProviderButton.scss'

import React, { useState } from 'react'

import { VenueProviderResponse } from 'apiClient/v1'
import { SynchronizationEvents } from 'core/FirebaseEvents/constants'
import { IVenue } from 'core/Venue'
import { IProviders } from 'core/Venue/types'
import useAnalytics from 'hooks/useAnalytics'
import { MoreCircleIcon } from 'icons'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import SelectInput from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared'
import { sortByLabel } from 'utils/strings'

import { DEFAULT_PROVIDER_OPTION } from '../utils/_constants'
import VenueProviderForm from '../VenueProviderForm/VenueProviderForm'

interface AddVenueProviderButtonProps {
  providers: IProviders[]
  setVenueProviders: (venueProviders: VenueProviderResponse[]) => void
  venue: IVenue
}

const AddVenueProviderButton = ({
  providers,
  setVenueProviders,
  venue,
}: AddVenueProviderButtonProps) => {
  const { logEvent } = useAnalytics()
  const [isCreationMode, setIsCreationMode] = useState(false)
  const [selectedProviderId, setSelectedProviderId] = useState(
    DEFAULT_PROVIDER_OPTION.value
  )
  const selectedProvider = providers.find(
    provider => provider.id.toString() === selectedProviderId
  )

  const providersOptions = sortByLabel(
    providers.map(item => ({
      value: item['id'].toString(),
      label: item['name'],
    }))
  )

  const setCreationMode = () => {
    logEvent?.(SynchronizationEvents.CLICKED_SYNCHRONIZE_OFFER, {
      offererId: venue.managingOfferer.nonHumanizedId,
      venueId: venue.nonHumanizedId,
    })
    setIsCreationMode(true)
  }

  const cancelProviderSelection = () => {
    setIsCreationMode(false)
    setSelectedProviderId(DEFAULT_PROVIDER_OPTION.value)
  }

  const afterSubmit = (venueProvider?: VenueProviderResponse) => {
    cancelProviderSelection()
    venueProvider && setVenueProviders([venueProvider])
  }

  const AddButton = (
    <div className="has-text-centered">
      <Button
        id="add-venue-provider-btn"
        onClick={setCreationMode}
        type="button"
        variant={ButtonVariant.SECONDARY}
        Icon={MoreCircleIcon}
      >
        Synchroniser des offres
      </Button>
    </div>
  )

  const VenueProviderSelection = (
    <>
      <FieldLayout label="Source" name="provider">
        <SelectInput
          defaultOption={DEFAULT_PROVIDER_OPTION}
          onChange={event => setSelectedProviderId(event.target.value)}
          name="provider"
          options={providersOptions}
          value={String(selectedProviderId)}
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

export default AddVenueProviderButton
