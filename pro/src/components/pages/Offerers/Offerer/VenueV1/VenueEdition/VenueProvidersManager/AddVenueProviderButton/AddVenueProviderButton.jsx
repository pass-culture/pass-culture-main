import './AddVenueProviderButton.scss'

import React, { useCallback, useMemo, useState } from 'react'

import { DEFAULT_PROVIDER_OPTION } from '../utils/_constants'
import PropTypes from 'prop-types'
import Select from 'components/layout/inputs/Select'
import { ReactComponent as SynchronizeOffers } from 'icons/ico-more-circle.svg'
import VenueProviderForm from '../VenueProviderForm'
import { sortByDisplayName } from 'utils/strings'

const AddVenueProviderButton = ({ providers, setVenueProviders, venue }) => {
  const [isCreationMode, setIsCreationMode] = useState(false)
  const [selectedProvider, setSelectedProvider] = useState(
    DEFAULT_PROVIDER_OPTION
  )
  const providersOptions = useMemo(
    () =>
      sortByDisplayName(
        providers.map(item => ({
          id: item['id'].toString(),
          displayName: item['name'],
        }))
      ),
    [providers]
  )

  const setCreationMode = useCallback(() => setIsCreationMode(true), [])

  const cancelProviderSelection = useCallback(() => {
    setIsCreationMode(false)
    setSelectedProvider(DEFAULT_PROVIDER_OPTION)
  }, [setIsCreationMode, setSelectedProvider])

  const handleChange = useCallback(
    event => {
      const selectedProvider = providers.find(
        provider => provider.id === event.target.value
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
      <button
        className="secondary-button"
        id="add-venue-provider-btn"
        onClick={setCreationMode}
        type="button"
      >
        <SynchronizeOffers />
        <span>Synchroniser des offres</span>
      </button>
    </div>
  )

  const VenueProviderSelection = (
    <>
      <Select
        defaultOption={DEFAULT_PROVIDER_OPTION}
        handleSelection={handleChange}
        label="Source"
        name="provider"
        options={providersOptions}
        selectedValue={selectedProvider.id}
      />
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
    id: PropTypes.string.isRequired,
    siret: PropTypes.string,
  }).isRequired,
}

export default AddVenueProviderButton
