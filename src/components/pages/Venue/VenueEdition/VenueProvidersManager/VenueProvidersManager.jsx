import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'

import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'
import * as pcapi from 'repository/pcapi/pcapi'

import AllocineProviderForm from './AllocineProviderForm/AllocineProviderForm'
import StocksProviderForm from './StocksProviderForm/StocksProviderForm'
import {
  ALLOCINE_PROVIDER_OPTION,
  DEFAULT_PROVIDER_OPTION,
  FNAC_PROVIDER_OPTION,
  LIBRAIRES_PROVIDER_OPTION,
  PRAXIEL_PROVIDER_OPTION,
  TITELIVE_PROVIDER_OPTION,
} from './utils/providerOptions'
import VenueProviderItem from './VenueProviderItem/VenueProviderItem'

const VenueProvidersManagerContainer = ({ notify, venue }) => {
  const [isCreationMode, setIsCreationMode] = useState(false)
  const [providerId, setProviderId] = useState(null)
  const [providers, setProviders] = useState([])
  const [venueProviders, setVenueProviders] = useState([])
  const [isAllocineProviderSelected, setIsAllocineProviderSelected] = useState(false)
  const [providerSelectedIsFnac, setProviderSelectedIsFnac] = useState(false)
  const [providerSelectedIsLibraires, setProviderSelectedIsLibraires] = useState(false)
  const [providerSelectedIsPraxiel, setProviderSelectedIsPraxiel] = useState(false)
  const [providerSelectedIsTitelive, setProviderSelectedIsTitelive] = useState(false)
  const [venueIdAtOfferProviderIsRequired, setVenueIdAtOfferProviderIsRequired] = useState(true)

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
      setProviderSelectedIsFnac(false)
      setProviderSelectedIsLibraires(false)
      setProviderSelectedIsPraxiel(false)
      setProviderSelectedIsTitelive(false)

      if (selectedProvider && selectedProvider.name === ALLOCINE_PROVIDER_OPTION.name) {
        setIsAllocineProviderSelected(true)
        setVenueIdAtOfferProviderIsRequired(selectedProvider.requireProviderIdentifier)
      } else if (selectedProvider && selectedProvider.name === TITELIVE_PROVIDER_OPTION.name) {
        setProviderSelectedIsTitelive(true)
      } else if (selectedProvider && selectedProvider.name === LIBRAIRES_PROVIDER_OPTION.name) {
        setProviderSelectedIsLibraires(true)
      } else if (selectedProvider && selectedProvider.name === FNAC_PROVIDER_OPTION.name) {
        setProviderSelectedIsFnac(true)
      } else if (selectedProvider && selectedProvider.name === PRAXIEL_PROVIDER_OPTION.name) {
        setProviderSelectedIsPraxiel(true)
      }

      setProviderId(selectedProviderId)
    },
    [providers]
  )

  const cancelProviderSelection = useCallback(() => {
    setIsCreationMode(false)
    setIsAllocineProviderSelected(false)
    setProviderSelectedIsFnac(false)
    setProviderSelectedIsLibraires(false)
    setProviderSelectedIsPraxiel(false)
    setProviderSelectedIsTitelive(false)
    setProviderId(null)
  }, [])

  const createVenueProvider = useCallback(
    payload => {
      pcapi
        .createVenueProvider(payload)
        .then(createdVenueProvider => {
          setVenueProviders([createdVenueProvider])
          setIsCreationMode(false)
        })
        .catch(error => {
          notify(error.errors)
          if (!isAllocineProviderSelected) {
            cancelProviderSelection()
          }
        })
    },
    [cancelProviderSelection, notify, isAllocineProviderSelected]
  )

  const hasAtLeastOneProvider = providers.length > 0
  const hasNoVenueProvider = venueProviders.length === 0
  const isStocksProvider =
    providerSelectedIsTitelive ||
    providerSelectedIsLibraires ||
    providerSelectedIsFnac ||
    providerSelectedIsPraxiel

  return (
    <div className="venue-providers-manager section">
      <h2 className="main-list-title">
        {'Importation d’offres'}
      </h2>

      <ul className="provider-list">
        {venueProviders.map(venueProvider => (
          <VenueProviderItem
            key={venueProvider.id}
            venueProvider={venueProvider}
          />
        ))}

        {isCreationMode && (
          <li className="add-provider-form">
            <div className="field-control">
              <div className="select-provider-section">
                <div className="select-source">
                  <label htmlFor="provider-options">
                    {'Source'}
                  </label>
                  <select
                    className="field-select"
                    id="provider-options"
                    onChange={handleChange}
                  >
                    <option
                      key={DEFAULT_PROVIDER_OPTION.id}
                      value={DEFAULT_PROVIDER_OPTION.id}
                    >
                      {DEFAULT_PROVIDER_OPTION.name}
                    </option>
                    {providers.map(provider => (
                      <option
                        key={`provider-${provider.id}`}
                        value={provider.id}
                      >
                        {provider.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            <div className="provider-form">
              {isAllocineProviderSelected && (
                <AllocineProviderForm
                  createVenueProvider={createVenueProvider}
                  providerId={providerId}
                  venueId={venue.id}
                  venueIdAtOfferProviderIsRequired={venueIdAtOfferProviderIsRequired}
                />
              )}

              {isStocksProvider && (
                <StocksProviderForm
                  createVenueProvider={createVenueProvider}
                  providerId={providerId}
                  siret={venue.siret}
                  venueId={venue.id}
                />
              )}
            </div>
          </li>
        )}
      </ul>

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
              {'Importer des offres'}
            </span>
          </button>
        </div>
      )}
    </div>
  )
}

VenueProvidersManagerContainer.propTypes = {
  notify: PropTypes.func.isRequired,
  venue: PropTypes.shape({
    id: PropTypes.string.isRequired,
    managingOffererId: PropTypes.string.isRequired,
    siret: PropTypes.string.isRequired,
  }).isRequired,
}

export default VenueProvidersManagerContainer
