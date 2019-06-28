import classnames from 'classnames'
import React, { Component } from 'react'
import { requestData } from 'redux-saga-data'
import { Field, Form } from 'react-final-form'
import { getRequestErrorStringFromErrors, showNotification } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import ReactTooltip from 'react-tooltip'
import Icon from '../../../layout/Icon'
import { HiddenField, TextField } from '../../../layout/form/fields'
import VenueProviderItem from './VenueProviderItem/VenueProviderItem'
import updateVenueIdAtOfferProvider from './decorators/updateVenueIdAtOfferProvider'
import checkIfProviderShouldBeDisabled from './utils/checkIfProviderShouldBeDisabled'

const DEFAULT_OPTION = {
  id: 'default',
  name: 'Choix de la source'
}

class VenueProvidersManager extends Component {
  constructor(props) {
    super(props)
    this.state = {
      isCreationMode: false,
      isLoadingMode: false,
      isProviderSelected: false,
      venueIdAtOfferProviderIsRequired: true
    }
  }

  componentDidUpdate() {
    ReactTooltip.rebuild()
  }

  static getDerivedStateFromProps(nextProps) {
    const {
      match: {
        params: {venueProviderId},
      },
    } = nextProps
    const isCreationMode = venueProviderId === 'nouveau'

    return {
      isCreationMode,
    }
  }

  addVenueProvider = () => {
    const {
      history,
      match: {
        params: {offererId, venueId},
      },
    } = this.props
    this.setState({
      isCreationMode: true
    })
    history.push(`/structures/${offererId}/lieux/${venueId}/fournisseurs/nouveau`)
  }

  loadProvidersAndVenueProviders = () => {
    const {
      dispatch,
      match: {
        params: {venueId},
      },
    } = this.props

    dispatch(
      requestData({
        apiPath: '/providers'
      })
    )
    dispatch(
      requestData({
        apiPath: `/venueProviders?venueId=${venueId}`,
      })
    )
  }

  resetFormState = () => {
    this.setState({
      isCreationMode: false,
      isLoadingMode: false,
      isProviderSelected: false,
      venueIdAtOfferProviderIsRequired: true
    })
  }

  handleSubmit = (formValues, form) => {
    const {dispatch} = this.props
    this.setState({
      isLoadingMode: true
    })
    const {
      id,
      provider,
      venueIdAtOfferProvider
    } = formValues
    const parsedProvider = JSON.parse(provider)

    const payload = {
      providerId: parsedProvider.id,
      venueIdAtOfferProvider,
      venueId: id
    }

    dispatch(requestData({
        apiPath: `/venueProviders`,
        body: payload,
        handleFail: this.handleFail(form),
        handleSuccess: this.handleSuccess,
        method: 'POST',
      })
    )
  }

  handleSuccess = () => {
    const {
      history,
      match: {
        params: {offererId, venueId},
      },
    } = this.props
    history.push(`/structures/${offererId}/lieux/${venueId}`)
  }

  handleFail = (form) => (state, action) => {
    const {dispatch} = this.props
    const {
      payload: {errors},
    } = action

    dispatch(showNotification({
      text: getRequestErrorStringFromErrors(errors),
      type: 'fail',
    }))
    this.resetFormInput(form)
    this.resetFormState()
  }

  resetFormInput = (form) => {
    form.batch(() => {
      form.change('provider', JSON.stringify(DEFAULT_OPTION))
    })
  }

  handleChange = (event, input) => {
    const valueFromSelectInput = event.target.value
    const valueParsed = JSON.parse(valueFromSelectInput)

    if (valueParsed && valueParsed.id !== DEFAULT_OPTION.id) {
      this.setState({
        isProviderSelected: true,
        venueIdAtOfferProviderIsRequired: valueParsed.requireProviderIdentifier
      })
    } else {
      this.resetFormState()
    }
    input.onChange(valueFromSelectInput)
  }

  componentDidMount() {
    this.loadProvidersAndVenueProviders()
  }

  render() {
    const {
      providers,
      venue,
      venueProviders,
    } = this.props
    const {
      isCreationMode,
      isLoadingMode,
      isProviderSelected,
      venueIdAtOfferProviderIsRequired
    } = this.state
    const decorators = [updateVenueIdAtOfferProvider]
    const hasAtLeastOneProvider = providers.length > 0

    return (
      <div className="venue-providers-manager section">
        <h2 className="main-list-title">
          IMPORTATIONS D'OFFRES
          <span className="is-pulled-right is-size-7 has-text-grey">
            Si vous avez plusieurs comptes auprès de la même source, ajoutez-les
            successivement.
          </span>
        </h2>

        <ul
          className="main-list">
          {venueProviders.map((venueProvider) => (
            <VenueProviderItem
              key={venueProvider.id}
              venueProvider={venueProvider}
            />
          ))}

          {isCreationMode && (
            <li>
              <Form
                decorators={decorators}
                initialValues={venue}
                onSubmit={this.handleSubmit}
                render={FormRendered({
                  handleChange: this.handleChange,
                  isProviderSelected,
                  isLoadingMode,
                  isCreationMode,
                  providers,
                  venueProviders,
                  venueIdAtOfferProviderIsRequired,
                })}
              />
            </li>
          )}
        </ul>

        {hasAtLeastOneProvider && (
          <div className="has-text-centered">
            <button
              className="button is-secondary"
              disabled={isCreationMode}
              id="add-venue-provider-btn"
              onClick={this.addVenueProvider}
              type="button"
            >
              + Importer des offres
            </button>
          </div>
        )}
      </div>
    )
  }
}

export const SelectRendered = ({
                                 handleChange,
                                 providers,
                                 venueProviders
                               }) => {
  return ({input}) => {
    return (
      <select
        {...input}
        className="field-select"
        onChange={(event) => handleChange(event, input)}
      >
        <option key={DEFAULT_OPTION.id}
                value={JSON.stringify(DEFAULT_OPTION)}>{DEFAULT_OPTION.name}
        </option>
        {providers.map((provider, index) => {
          const isProviderDisabled = checkIfProviderShouldBeDisabled(venueProviders, provider)

          return (
            <option disabled={isProviderDisabled}
                    key={index}
                    value={JSON.stringify(provider)}>{provider.name}
            </option>
          )
        })}
      </select>
    )
  }
}

export const FormRendered = ({
                               handleChange,
                               isProviderSelected,
                               isLoadingMode,
                               isCreationMode,
                               providers,
                               venueProviders,
                               venueIdAtOfferProviderIsRequired
                             }) => {
  return ({handleSubmit}) => {
    return (
      <form onSubmit={handleSubmit}>
        <div className="venue-provider-table">
          <HiddenField name="id"/>
          <div className="provider-container">
            <div className="provider-picto">
              <span className="field picto">
                <Icon svg="picto-db-default"/>
              </span>
            </div>

            <Field
              name="provider"
              required
              render={SelectRendered({handleChange, providers, venueProviders})}>
            </Field>
          </div>

          {isProviderSelected && (
            <div className="venue-id-at-offer-provider-container">
              <TextField
                className={classnames('field-text fs12', {
                  'field-is-read-only': !venueIdAtOfferProviderIsRequired || isLoadingMode,
                })}
                label="Compte : "
                name="venueIdAtOfferProvider"
                readOnly={!venueIdAtOfferProviderIsRequired || isLoadingMode}
                required
              />

              {!isLoadingMode && venueIdAtOfferProviderIsRequired && (
                <span
                  className="tooltip tooltip-info"
                  data-place="bottom"
                  data-tip={`<p>Veuillez saisir un identifiant.</p>`}
                >
                  <Icon svg="picto-info"/>
                </span>
              )}
            </div>
          )}

          {isProviderSelected && isCreationMode && !isLoadingMode && (
            <div className="provider-import-button-container">
              <button
                className="button is-intermediate provider-import-button"
                type="submit"
              >
                Importer
              </button>
            </div>
          )}
        </div>
      </form>
    )
  }
}

VenueProvidersManager.propTypes = {
  dispatch: PropTypes.func,
  history: PropTypes.shape(),
  match: PropTypes.shape({
    params: PropTypes.shape()
  }),
  providers: PropTypes.array,
  venue: PropTypes.shape(),
  venueProviders: PropTypes.array
}

export default VenueProvidersManager
