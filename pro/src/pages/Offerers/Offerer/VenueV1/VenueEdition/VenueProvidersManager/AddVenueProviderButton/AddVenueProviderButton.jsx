import './AddVenueProviderButton.scss'

import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import { SynchronizationEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { MoreCircleIcon } from 'icons'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import SelectInput from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared'
import { sortByLabel } from 'utils/strings'

import { DEFAULT_PROVIDER_OPTION } from '../utils/_constants'
import VenueProviderForm from '../VenueProviderForm/VenueProviderForm'

const AddVenueProviderButton = ({ providers, setVenueProviders, venue }) => {
  const { logEvent } = useAnalytics()
  const [isCreationMode, setIsCreationMode] = useState(false)
  const [selectedProvider, setSelectedProvider] = useState(
    DEFAULT_PROVIDER_OPTION
  )
  const providersOptions = sortByLabel(
    providers.map(item => ({
      value: item['id'].toString(),
      label: item['name'],
    }))
  )

  const setCreationMode = useCallback(() => {
    logEvent?.(SynchronizationEvents.CLICKED_SYNCHRONIZE_OFFER, {
      offererId: venue.managingOfferer.nonHumanizedId,
      venueId: venue.nonHumanizedId,
    })
    setIsCreationMode(true)
  }, [])

  const cancelProviderSelection = useCallback(() => {
    setIsCreationMode(false)
    setSelectedProvider(DEFAULT_PROVIDER_OPTION)
  }, [setIsCreationMode, setSelectedProvider])

  const handleChange = useCallback(
    event => {
      const selectedProvider = providers.find(
        provider => provider.id.toString() === event.target.value
      )
      setSelectedProvider(
        selectedProvider ? selectedProvider : DEFAULT_PROVIDER_OPTION
      )
    },
    [providers]
  )

  const afterSubmit = useCallback(
    venueProvider => {
      cancelProviderSelection()
      venueProvider && setVenueProviders([venueProvider])
    },
    [cancelProviderSelection, setVenueProviders]
  )

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
          onChange={handleChange}
          name="provider"
          options={providersOptions}
          value={selectedProvider.value.toString()}
        />
      </FieldLayout>

      {selectedProvider.id !== DEFAULT_PROVIDER_OPTION.id && (
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

AddVenueProviderButton.defaultProps = {
  providers: [],
}

AddVenueProviderButton.propTypes = {
  providers: PropTypes.arrayOf(PropTypes.shape()),
  setVenueProviders: PropTypes.func.isRequired,
  venue: PropTypes.shape({
    nonHumanizedId: PropTypes.number.isRequired,
    siret: PropTypes.string,
  }).isRequired,
}

export default AddVenueProviderButton
