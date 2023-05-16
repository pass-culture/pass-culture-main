import './AddVenueProviderButton.scss'

import PropTypes from 'prop-types'
import React, { useCallback, useMemo, useState } from 'react'

import { MoreCircleIcon } from 'icons'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Select from 'ui-kit/form_raw/Select'
import { sortByDisplayName } from 'utils/strings'

import { DEFAULT_PROVIDER_OPTION } from '../utils/_constants'
import VenueProviderForm from '../VenueProviderForm/VenueProviderForm'

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
      <Select
        defaultOption={DEFAULT_PROVIDER_OPTION}
        handleSelection={handleChange}
        label="Source"
        name="provider"
        options={providersOptions}
        selectedValue={selectedProvider.id.toString()}
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
