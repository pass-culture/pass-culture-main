import PropTypes from 'prop-types'
import React, { Component } from 'react'

import Spinner from 'components/layout/Spinner'

class StocksProviderForm extends Component {
  constructor() {
    super()

    this.state = {
      isCheckingApi: false,
    }
  }

  handleFormSubmit = event => {
    event.preventDefault()

    this.setState({ isCheckingApi: true })

    const { createVenueProvider, providerId, venueId, siret } = this.props
    const payload = {
      providerId,
      venueIdAtOfferProvider: siret,
      venueId,
    }

    createVenueProvider(payload)
      .then(() => {
        const { historyPush, offererId, venueId } = this.props

        historyPush(`/structures/${offererId}/lieux/${venueId}`)
      })
      .catch(error => {
        error.json().then(body => {
          const { cancelProviderSelection, notify } = this.props

          notify(body)
          cancelProviderSelection()
        })
      })
  }

  render() {
    const { siret } = this.props
    const { isCheckingApi } = this.state

    if (isCheckingApi) {
      return <Spinner message="Vérification de votre rattachement" />
    } else {
      return (
        <form
          className="provider-form"
          onSubmit={this.handleFormSubmit}
        >
          <div className="account-section">
            <div className="account-label">
              {'Compte'}
            </div>
            <div className="account-value">
              {siret}
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
      )
    }
  }
}

StocksProviderForm.propTypes = {
  cancelProviderSelection: PropTypes.func.isRequired,
  createVenueProvider: PropTypes.func.isRequired,
  historyPush: PropTypes.func.isRequired,
  notify: PropTypes.func.isRequired,
  offererId: PropTypes.string.isRequired,
  providerId: PropTypes.string.isRequired,
  siret: PropTypes.string.isRequired,
  venueId: PropTypes.string.isRequired,
}

export default StocksProviderForm
