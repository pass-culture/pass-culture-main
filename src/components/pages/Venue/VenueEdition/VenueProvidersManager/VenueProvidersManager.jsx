import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import ReactTooltip from 'react-tooltip'

import AllocineProviderForm from './AllocineProviderForm/AllocineProviderFormContainer'
import LibrairesProviderForm from './LibrairesProviderForm/LibrairesProviderFormContainer'
import TiteliveProviderForm from './TiteliveProviderForm/TiteliveProviderFormContainer'
import FnacProviderForm from './FnacProviderForm/FnacProviderFormContainer'
import {
  ALLOCINE_PROVIDER_OPTION,
  DEFAULT_PROVIDER_OPTION,
  FNAC_PROVIDER_OPTION,
  LIBRAIRES_PROVIDER_OPTION,
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
      providerSelectedIsTitelive: false,
      providerSelectedIsLibraires: false,
      providerSelectedIsFnac: false,
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
    const valueFromSelectInput = event.target.value
    const valueParsed = JSON.parse(valueFromSelectInput)
    this.setState({
      providerSelectedIsAllocine: false,
      providerSelectedIsTitelive: false,
      providerSelectedIsLibraires: false,
      providerSelectedIsFnac: false,
    })

    if (valueParsed && valueParsed.name === ALLOCINE_PROVIDER_OPTION.name) {
      this.setState({
        providerSelectedIsAllocine: true,
        venueIdAtOfferProviderIsRequired: valueParsed.requireProviderIdentifier,
      })
    } else if (valueParsed && valueParsed.name === TITELIVE_PROVIDER_OPTION.name) {
      this.setState({
        providerSelectedIsTitelive: true,
      })
    } else if (valueParsed && valueParsed.name === LIBRAIRES_PROVIDER_OPTION.name) {
      this.setState({
        providerSelectedIsLibraires: true,
      })
    } else if (valueParsed && valueParsed.name === FNAC_PROVIDER_OPTION.name) {
      this.setState({
        providerSelectedIsFnac: true,
      })
    }

    this.setState({
      providerId: valueParsed.id,
    })
  }

  cancelProviderSelection = () => {
    this.toggleOffCreationMode()
    this.setState({
      providerSelectedIsTitelive: false,
      providerSelectedIsLibraires: false,
      providerSelectedIsFnac: false,
      providerId: null,
    })
  }

  render() {
    const { providers, match, venueProviders, venueSiret } = this.props
    const {
      isCreationMode,
      providerId,
      providerSelectedIsAllocine,
      providerSelectedIsTitelive,
      providerSelectedIsLibraires,
      providerSelectedIsFnac,
      venueIdAtOfferProviderIsRequired,
    } = this.state
    const hasAtLeastOneProvider = providers.length > 0
    const hasNoVenueProvider = venueProviders.length === 0

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
                        value={JSON.stringify(DEFAULT_PROVIDER_OPTION)}
                      >
                        {DEFAULT_PROVIDER_OPTION.name}
                      </option>
                      {providers.map(provider => (
                        <option
                          key={`provider-${provider.id}`}
                          value={JSON.stringify(provider)}
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
                    offererId={match.params.offererId}
                    providerId={providerId}
                    venueId={match.params.venueId}
                    venueIdAtOfferProviderIsRequired={venueIdAtOfferProviderIsRequired}
                  />
                )}

                {providerSelectedIsTitelive && (
                  <TiteliveProviderForm
                    cancelProviderSelection={this.cancelProviderSelection}
                    offererId={match.params.offererId}
                    providerId={providerId}
                    venueId={match.params.venueId}
                    venueSiret={venueSiret}
                  />
                )}

                {providerSelectedIsLibraires && (
                  <LibrairesProviderForm
                    cancelProviderSelection={this.cancelProviderSelection}
                    offererId={match.params.offererId}
                    providerId={providerId}
                    venueId={match.params.venueId}
                    venueSiret={venueSiret}
                  />
                )}

                {providerSelectedIsFnac && (
                  <FnacProviderForm
                    cancelProviderSelection={this.cancelProviderSelection}
                    offererId={match.params.offererId}
                    providerId={providerId}
                    venueId={match.params.venueId}
                    venueSiret={venueSiret}
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
              {'+ Importer des offres'}
            </button>
          </div>
        )}
      </div>
    )
  }
}

VenueProvidersManager.propTypes = {
  loadProvidersAndVenueProviders: PropTypes.func.isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape(),
  }).isRequired,
  providers: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  venueProviders: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  venueSiret: PropTypes.string.isRequired,
}

export default VenueProvidersManager
