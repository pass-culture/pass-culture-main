/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useMemo, useState } from 'react'

import Select, { buildSelectOptions } from 'components/layout/inputs/Select'
import { isAllocineProvider } from 'components/pages/Offers/domain/localProvider'
import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'
import * as pcapi from 'repository/pcapi/pcapi'

import AllocineProviderForm from './AllocineProviderForm/AllocineProviderForm'
import StocksProviderForm from './StocksProviderForm/StocksProviderForm'
import { DEFAULT_PROVIDER_OPTION } from './utils/_constants'
import VenueProviderItem from './VenueProviderItem/VenueProviderItem'

import './VenueProvidersManager.scss'

const VenueProvidersManagerContainer = ({ notifyError, notifySuccess, venue }) => {
  const [isCreationMode, setIsCreationMode] = useState(false)
  const [selectedProviderId, setSelectedProviderId] = useState(DEFAULT_PROVIDER_OPTION.id)
  const [providers, setProviders] = useState([])
  const [venueProviders, setVenueProviders] = useState([])
  const [isAllocineProviderSelected, setIsAllocineProviderSelected] = useState(false)

  useEffect(() => {
    pcapi.loadProviders(venue.id).then(providers => setProviders(providers))
    pcapi.loadVenueProviders(venue.id).then(venueProviders => setVenueProviders(venueProviders))
  }, [venue.id])

  useEffect(() => {
    if (venueProviders.length > 0) {
      setIsCreationMode(false)
    }
  }, [venueProviders])

  const toggleOnCreationMode = useCallback(() => setIsCreationMode(true), [])

  const handleChange = useCallback(
    event => {
      const selectedProviderId = event.target.value
      const selectedProvider = providers.find(provider => provider.id === selectedProviderId)
      setIsAllocineProviderSelected(false)
      setSelectedProviderId(selectedProviderId)

      if (isAllocineProvider(selectedProvider)) {
        setIsAllocineProviderSelected(true)
      }
    },
    [providers]
  )

  const cancelProviderSelection = useCallback(() => {
    setIsCreationMode(false)
    setIsAllocineProviderSelected(false)
    setSelectedProviderId(null)
  }, [])

  const createVenueProvider = useCallback(
    payload => {
      pcapi
        .createVenueProvider(payload)
        .then(createdVenueProvider => {
          setVenueProviders([createdVenueProvider])
          setIsCreationMode(false)
          notifySuccess()
        })
        .catch(error => {
          notifyError(error.errors)
          if (!isAllocineProviderSelected) {
            cancelProviderSelection()
          }
        })
    },
    [cancelProviderSelection, notifyError, notifySuccess, isAllocineProviderSelected]
  )

  const hasAtLeastOneProvider = providers.length > 0
  const hasNoVenueProvider = venueProviders.length === 0

  const providersOptions = useMemo(() => buildSelectOptions('id', 'name', providers), [providers])

  return (
    <div className="venue-providers-manager section">
      <h2 className="main-list-title">
        Importation d’offres
      </h2>

      <ul className="provider-list">
        {venueProviders.map(venueProvider => (
          <VenueProviderItem
            key={venueProvider.id}
            venueDepartmentCode={venue.departementCode}
            venueProvider={venueProvider}
          />
        ))}
      </ul>

      {isCreationMode && (
        <>
          <Select
            defaultOption={DEFAULT_PROVIDER_OPTION}
            handleSelection={handleChange}
            label="Source"
            name="provider"
            options={providersOptions}
            selectedValue={selectedProviderId}
          />
          {selectedProviderId !== DEFAULT_PROVIDER_OPTION.id &&
            (isAllocineProviderSelected ? (
              <AllocineProviderForm
                createVenueProvider={createVenueProvider}
                providerId={selectedProviderId}
                venueId={venue.id}
              />
            ) : (
              <StocksProviderForm
                createVenueProvider={createVenueProvider}
                providerId={selectedProviderId}
                siret={venue.siret}
                venueId={venue.id}
              />
            ))}
        </>
      )}

      {hasAtLeastOneProvider && hasNoVenueProvider && !isCreationMode && (
        <div className="has-text-centered">
          <button
            className="secondary-button"
            id="add-venue-provider-btn"
            onClick={toggleOnCreationMode}
            type="button"
          >
            <AddOfferSvg />
            <span>
              Importer des offres
            </span>
          </button>
        </div>
      )}
    </div>
  )
}

VenueProvidersManagerContainer.propTypes = {
  notifyError: PropTypes.func.isRequired,
  notifySuccess: PropTypes.func.isRequired,
  venue: PropTypes.shape({
    id: PropTypes.string.isRequired,
    managingOffererId: PropTypes.string.isRequired,
    siret: PropTypes.string.isRequired,
    departementCode: PropTypes.string.isRequired,
  }).isRequired,
}

export default VenueProvidersManagerContainer
