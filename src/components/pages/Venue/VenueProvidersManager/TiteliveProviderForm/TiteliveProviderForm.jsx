import React, {PureComponent} from 'react'
import {Form} from 'react-final-form'
import PropTypes from 'prop-types'

class TiteliveProviderForm extends PureComponent {
  constructor() {
    super()
    this.state = {
      isLoadingMode: false,
    }
  }

  handleFormSubmit = (formValues, form) => {
    this.setState({ isLoadingMode: true })

    const { createVenueProvider } = this.props
    const { providerId, venueId, venueSiret } = this.props

    const payload = {
      providerId: providerId,
      venueIdAtOfferProvider: venueSiret,
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
    const { venueSiret } = this.props
    const { isLoadingMode } = this.state
    return (
      <form onSubmit={props.handleSubmit}>
        <div className="titelive-provider-form">
          <div className="compte-section">
            <div className="account-label">
              {'Compte'}
            </div>
            <div
              className='account-value'
            >
              {venueSiret}
            </div>
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
  venueSiret: PropTypes.string.isRequired
}

export default TiteliveProviderForm
