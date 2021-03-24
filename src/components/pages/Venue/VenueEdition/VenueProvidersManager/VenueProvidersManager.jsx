import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import ReactTooltip from 'react-tooltip'

import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'

import AllocineProviderForm from './AllocineProviderForm/AllocineProviderFormContainer'
import StocksProviderForm from './StocksProviderForm/StocksProviderFormContainer'
import {
  ALLOCINE_PROVIDER_OPTION,
  DEFAULT_PROVIDER_OPTION,
  FNAC_PROVIDER_OPTION,
  LIBRAIRES_PROVIDER_OPTION,
  PRAXIEL_PROVIDER_OPTION,
  TITELIVE_PROVIDER_OPTION,
} from './utils/providerOptions'
import VenueProviderItem from './VenueProviderItem/VenueProviderItem'

class VenueProvidersManager extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      isCreationMode: false,
      providerId: null,
      providerSelectedIsAllocine: false,
      providerSelectedIsFnac: false,
      providerSelectedIsLibraires: false,
      providerSelectedIsPraxiel: false,
      providerSelectedIsTitelive: false,
      venueIdAtOfferProviderIsRequired: true,
    }
  }

  componentDidMount() {
    const { loadProvidersAndVenueProviders } = this.props
    loadProvidersAndVenueProviders()
  }

  componentDidUpdate(prevProps) {
    ReactTooltip.rebuild()
    const { venueProviders } = this.props
    if (prevProps.venueProviders.length < venueProviders.length) {
      this.toggleOffCreationMode()
    }
  }

  toggleOffCreationMode = () => {
    this.setState({ isCreationMode: false })
  }

  toggleOnCreationMode = () => {
    this.setState({
      isCreationMode: true,
    })
  }

  handleChange = event => {
    const { providers } = this.props
    const selectedProviderId = event.target.value
    const selectedProvider = providers.find(provider => provider.id === selectedProviderId)
    this.setState({
      providerSelectedIsAllocine: false,
      providerSelectedIsFnac: false,
      providerSelectedIsLibraires: false,
      providerSelectedIsPraxiel: false,
      providerSelectedIsTitelive: false,
    })

    if (selectedProvider && selectedProvider.name === ALLOCINE_PROVIDER_OPTION.name) {
      this.setState({
        providerSelectedIsAllocine: true,
        venueIdAtOfferProviderIsRequired: selectedProvider.requireProviderIdentifier,
      })
    } else if (selectedProvider && selectedProvider.name === TITELIVE_PROVIDER_OPTION.name) {
      this.setState({
        providerSelectedIsTitelive: true,
      })
    } else if (selectedProvider && selectedProvider.name === LIBRAIRES_PROVIDER_OPTION.name) {
      this.setState({
        providerSelectedIsLibraires: true,
      })
    } else if (selectedProvider && selectedProvider.name === FNAC_PROVIDER_OPTION.name) {
      this.setState({
        providerSelectedIsFnac: true,
      })
    } else if (selectedProvider && selectedProvider.name === PRAXIEL_PROVIDER_OPTION.name) {
      this.setState({
        providerSelectedIsPraxiel: true,
      })
    }

    this.setState({
      providerId: selectedProviderId,
    })
  }

  cancelProviderSelection = () => {
    this.toggleOffCreationMode()
    this.setState({
      providerSelectedIsFnac: false,
      providerSelectedIsLibraires: false,
      providerSelectedIsPraxiel: false,
      providerSelectedIsTitelive: false,
      providerId: null,
    })
  }

  render() {
    const { history, providers, venueProviders, venue } = this.props
    const {
      isCreationMode,
      providerId,
      providerSelectedIsAllocine,
      providerSelectedIsFnac,
      providerSelectedIsLibraires,
      providerSelectedIsPraxiel,
      providerSelectedIsTitelive,
      venueIdAtOfferProviderIsRequired,
    } = this.state
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
                      onBlur={this.handleChange}
                      onChange={this.handleChange}
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
                {providerSelectedIsAllocine && (
                  <AllocineProviderForm
                    offererId={venue.managingOffererId}
                    providerId={providerId}
                    venueId={venue.id}
                    venueIdAtOfferProviderIsRequired={venueIdAtOfferProviderIsRequired}
                  />
                )}

                {isStocksProvider && (
                  <StocksProviderForm
                    cancelProviderSelection={this.cancelProviderSelection}
                    historyPush={history.push}
                    offererId={venue.managingOffererId}
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
              onClick={this.toggleOnCreationMode}
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
}

VenueProvidersManager.propTypes = {
  history: PropTypes.shape().isRequired,
  loadProvidersAndVenueProviders: PropTypes.func.isRequired,
  providers: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  venue: PropTypes.shape({
    id: PropTypes.string.isRequired,
    managingOffererId: PropTypes.string.isRequired,
    siret: PropTypes.string.isRequired,
  }).isRequired,
  venueProviders: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default VenueProvidersManager
