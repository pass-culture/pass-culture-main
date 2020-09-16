import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form } from 'react-final-form'

class FnacProviderForm extends PureComponent {
  constructor() {
    super()
    this.state = {
      isLoadingMode: false,
    }
  }

  handleFormSubmit = () => {
    this.setState({ isLoadingMode: true })

    const { createVenueProvider } = this.props
    return createVenueProvider(this.handleFail, this.handleSuccess)
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
      <form onSubmit={props.handleSubmit}>
        <div className="provider-form">
          <div className="account-section">
            <div className="account-label">
              {'Compte'}
            </div>
            <div className="account-value">
              {venueSiret}
            </div>
          </div>

          {!isLoadingMode && (
            <div className="provider-import-button-container">
              <button
                className="secondary-button"
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

FnacProviderForm.propTypes = {
  cancelProviderSelection: PropTypes.func.isRequired,
  createVenueProvider: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  notify: PropTypes.func.isRequired,
  venueId: PropTypes.string.isRequired,
  venueSiret: PropTypes.string.isRequired,
}

export default FnacProviderForm
