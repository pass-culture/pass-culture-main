import PropTypes from 'prop-types'
import React, { useCallback, useMemo, useState } from 'react'

import Select, { buildSelectOptions } from 'components/layout/inputs/Select'
import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'

import { DEFAULT_PROVIDER_OPTION } from '../utils/_constants'
import VenueProviderForm from '../VenueProviderForm'

const AddVenueProviderButton = ({ providers, setVenueProviders, venue }) => {
  const [isCreationMode, setIsCreationMode] = useState(false)
  const [selectedProvider, setSelectedProvider] = useState(
    DEFAULT_PROVIDER_OPTION
  )
  const providersOptions = useMemo(
    () => buildSelectOptions('id', 'name', providers),
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
        <AddOfferSvg />
        <span>Importer des offres</span>
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
