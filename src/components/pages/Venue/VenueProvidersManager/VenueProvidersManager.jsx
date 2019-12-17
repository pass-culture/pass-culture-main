import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import VenueProviderItem from './VenueProviderItem/VenueProviderItem'
import { ALLOCINE_PROVIDER_OPTION, DEFAULT_PROVIDER_OPTION } from './utils/utils'
import checkIfProviderShouldBeDisabled from './utils/checkIfProviderShouldBeDisabled'
import AllocineProviderForm from './AllocineProviderForm/AllocineProviderFormContainer'
import TiteliveProviderForm from './TiteliveProviderForm/TiteliveProviderFormContainer'

class VenueProvidersManager extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      isCreationMode: false,
      isLoadingMode: false,
      isProviderSelected: false,
      providerId: null,
      providerSelectedIsAllocine: false,
      venueIdAtOfferProviderIsRequired: true,
    }
  }

  componentDidMount() {
    const { loadProvidersAndVenueProviders } = this.props
    loadProvidersAndVenueProviders()
  }

  handleAddVenueProvider = () => {
    this.setState({
      isCreationMode: true,
    })
  }

  handleChange = event => {
    const valueFromSelectInput = event.target.value
    const valueParsed = JSON.parse(valueFromSelectInput)

    if (valueParsed && valueParsed.id !== DEFAULT_PROVIDER_OPTION.id) {
      this.setState({
        isProviderSelected: true,
        venueIdAtOfferProviderIsRequired: valueParsed.requireProviderIdentifier,
      })
    }

    if (valueParsed && valueParsed.name === ALLOCINE_PROVIDER_OPTION.name) {
      this.setState({
        providerSelectedIsAllocine: true,
      })
    } else {
      this.setState({
        providerSelectedIsAllocine: false,
      })
    }

    if (valueParsed && valueParsed.id == DEFAULT_PROVIDER_OPTION.id) {
      this.setState({
        isProviderSelected: false,
        venueIdAtOfferProviderIsRequired: valueParsed.requireProviderIdentifier,
      })
    }

    this.setState({
      providerId: valueParsed.id,
    })
  }

  render() {
    const { providers, match, venueProviders } = this.props
    const {
      isCreationMode,
      isLoadingMode,
      isProviderSelected,
      providerId,
      providerSelectedIsAllocine,
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
              <div className="select-provider-section">
                <div id="select-source">
                  <label htmlFor="provider-options">
                    {'Source'}
                  </label>
                  <select
                    className="field-select"
                    id="provider-options"
                    onChange={this.handleChange}
                  >
                    <option
                      key={DEFAULT_PROVIDER_OPTION.id}
                      value={JSON.stringify(DEFAULT_PROVIDER_OPTION)}
                    >
                      {DEFAULT_PROVIDER_OPTION.name}
                    </option>
                    {providers.map(provider => {
                      const isProviderDisabled = checkIfProviderShouldBeDisabled(
                        venueProviders,
                        provider
                      )

                      return (
                        <option
                          disabled={isProviderDisabled}
                          key={`provider-${provider.id}`}
                          value={JSON.stringify(provider)}
                        >
                          {provider.name}
                        </option>
                      )
                    })}
                  </select>
                </div>
              </div>
              <div className="provider-form">
                {providerSelectedIsAllocine && (
                  <AllocineProviderForm
                    isCreationMode={isCreationMode}
                    isLoadingMode={isLoadingMode}
                    providerId={providerId}
                    venueId={match.params.venueId}
                    venueIdAtOfferProviderIsRequired={venueIdAtOfferProviderIsRequired}
                  />
                )}

                {!providerSelectedIsAllocine && isProviderSelected && (
                  <TiteliveProviderForm
                    isCreationMode={isCreationMode}
                    providerId={providerId}
                    venueId={match.params.venueId}
                    venueIdAtOfferProviderIsRequired={venueIdAtOfferProviderIsRequired}
                  />
                )}
              </div>
            </li>
          )}
        </ul>

        {hasAtLeastOneProvider && hasNoVenueProvider &&(
          <div className="has-text-centered">
            <button
              className="button is-secondary"
              disabled={isCreationMode}
              id="add-venue-provider-btn"
              onClick={this.handleAddVenueProvider}
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
}

export default VenueProvidersManager
