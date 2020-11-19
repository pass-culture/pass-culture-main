import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import { Form } from 'react-final-form'

import Spinner from 'components/layout/Spinner'

class StocksProviderForm extends Component {
  constructor() {
    super()
    this.state = {
      isLoadingMode: false,
    }
  }

  handleFormSubmit = () => {
    this.setState({ isLoadingMode: true })

    const { createVenueProvider } = this.props
    const { providerId, venueId, venueSiret } = this.props

    const payload = {
      providerId: providerId,
      venueIdAtOfferProvider: venueSiret,
      venueId: venueId,
    }

    return createVenueProvider(this.handleFail, this.handleSuccess, payload)
  }

  handleSuccess = () => {
    const { history, offererId, venueId } = this.props
    history.push(`/structures/${offererId}/lieux/${venueId}`)
  }

  handleFail = (state, action) => {
    const { cancelProviderSelection, notify } = this.props
    const {
      payload: { errors },
    } = action
    notify(errors)
    cancelProviderSelection()
  }

  renderForm = props => {
    const { venueSiret } = this.props
    const { isLoadingMode } = this.state
    return (
      <Fragment>
        {isLoadingMode && <Spinner sentence="Vérification de votre rattachement" />}

        {!isLoadingMode && (
          <form
            className="provider-form"
            onSubmit={props.handleSubmit}
          >
            <div className="account-section">
              <div className="account-label">
                {'Compte'}
              </div>
              <div className="account-value">
                {venueSiret}
              </div>
            </div>
            <div className="provider-import-button-container">
              <button
                className="secondary-button"
                type="submit"
              >
                {'Importer'}
              </button>
            </div>
          </form>
        )}
      </Fragment>
    )
  }

  render() {
    return (
      <Form
        onSubmit={this.handleFormSubmit}
        render={this.renderForm}
      />
    )
  }
}

StocksProviderForm.propTypes = {
  cancelProviderSelection: PropTypes.func.isRequired,
  createVenueProvider: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  notify: PropTypes.func.isRequired,
  providerId: PropTypes.string.isRequired,
  venueId: PropTypes.string.isRequired,
  venueSiret: PropTypes.string.isRequired,
}

export default StocksProviderForm
