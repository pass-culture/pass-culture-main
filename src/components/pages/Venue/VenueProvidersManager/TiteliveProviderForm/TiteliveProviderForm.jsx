import classNames from 'classnames'
import React, {PureComponent} from 'react'
import {Form} from 'react-final-form'

import TextField from '../../../../layout/form/fields/TextField'
import Icon from '../../../../layout/Icon'
import PropTypes from 'prop-types'

class TiteliveProviderForm extends PureComponent {
  constructor() {
    super()
    this.state = {
      isLoadingMode: false,
    }
  }

  handleFormSubmit = (formValues, form) => {
    formValues.preventDefault()
    this.setState({ isLoadingMode: true })

    const { createVenueProvider } = this.props
    const { venueIdAtOfferProvider } = formValues
    const { providerId, venueId } = this.props

    const payload = {
      providerId: providerId,
      venueIdAtOfferProvider,
      venueId: venueId,
    }

    return createVenueProvider(this.handleFail(form), this.handleSuccess, payload)
  }

  handleSuccess = () => {
    const {
      history,
      offererId,
      venueId,
    } = this.props
    history.push(`/structures/${offererId}/lieux/${venueId}`)
  }

  handleFail = () => (state, action) => {
    const { notify } = this.props
    const {
      payload: { errors },
    } = action

    notify(errors)
  }

  renderForm = props => {
    const { venueIdAtOfferProviderIsRequired } = this.props
    const { isLoadingMode } = this.state
    return (
      <form onSubmit={props.handleSubmit}>
        <div className="titelive-provider-form">
          <div className="compte-section">
            <div className="label-section">
              <label htmlFor="venueIdAtOfferProvider">
                {'Compte'}
              </label>
              {!isLoadingMode && venueIdAtOfferProviderIsRequired && (
                <span
                  className="tooltip tooltip-info"
                  data-place="bottom"
                  data-tip={`<p>Veuillez saisir un compte.</p>`}
                >
                  <Icon
                    alt="image d’aide à l’information"
                    svg="picto-info"
                  />
                </span>
              )}
            </div>

            <TextField
              className={classNames('field-text', {
                'field-is-read-only': !venueIdAtOfferProviderIsRequired || isLoadingMode,
              })}
              name="venueIdAtOfferProvider"
              readOnly={!venueIdAtOfferProviderIsRequired || isLoadingMode}
              required
            />
          </div>

          {!isLoadingMode && (
            <div className="provider-import-button-container">
              <button
                className="button is-intermediate provider-import-button"
                type="submit"
              >
                {'Importer'}
              </button>
            </div>
          )}
        </div>
      </form>
    )
  }

  render() {
    return (<Form
      onSubmit={this.handleFormSubmit}
      render={this.renderForm}
            />)
  }
}

TiteliveProviderForm.propTypes = {
  createVenueProvider: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  notify: PropTypes.func.isRequired,
  providerId: PropTypes.string.isRequired,
  venueId: PropTypes.string.isRequired,
  venueIdAtOfferProviderIsRequired: PropTypes.bool.isRequired,
}

export default TiteliveProviderForm
