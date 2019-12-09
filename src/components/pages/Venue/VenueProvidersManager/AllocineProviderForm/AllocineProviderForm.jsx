import classNames from 'classnames'
import React, {PureComponent} from 'react'
import PropTypes from 'prop-types'
import TextField from '../../../../layout/form/fields/TextField'
import NumberField from '../../../../layout/form/fields/NumberField'
import Icon from '../../../../layout/Icon'
import {Form} from 'react-final-form'
import SynchronisationConfirmationModal from './SynchronisationConfirmationModal/SynchronisationConfirmationModal'

class AllocineProviderForm extends PureComponent {
  constructor() {
    super()
    this.state = {
      isLoadingMode: false,
      isShowingConfirmationModal: false,
    }
  }

  handleSubmit = (formValues, form) => {
    const {createVenueProvider} = this.props

    console.log("----------------")
    console.log({formValues})
    const { venueIdAtOfferProvider } = formValues

    const { providerId, venueId } = this.props

    const payload = {
      price: null,
      providerId: providerId,
      venueIdAtOfferProvider,
      venueId: venueId,
    }

    this.setState({ isLoadingMode: true })

    createVenueProvider(this.handleFail(form), this.handleSuccess, payload)
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

  handleFail = () => (state, action) => {
    const {notify} = this.props
    const {
      payload: {errors},
    } = action

    notify(errors)
  }

  handleShowModal = () => {
    this.setState({
      isShowingConfirmationModal: true,
    })
  }

  hideModal = () => {
    this.setState({
      isShowingConfirmationModal: false,
    })
  }

  renderForm = () => {
    const { venueIdAtOfferProviderIsRequired} = this.props
    const { isLoadingMode } = this.state

    return (
      <div className="allocine-provider-form">
        <div className="compte-section">
          <div>
            <label
              className="label-text"
              htmlFor="venueIdAtOfferProvider"
            >
              {'Compte'}
            </label>
            {!isLoadingMode && venueIdAtOfferProviderIsRequired && (
              <span
                className="tooltip tooltip-info"
                data-place="bottom"
                data-tip={`<p>Veuillez saisir un compte.</p>`}
                id="compte-tooltip"
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
          <div className="price-section">
            <div>
              <label
                className="label-prix"
                htmlFor="price"
              >
                {'Prix de vente/place'}
              </label>
              <span
                className="tooltip tooltip-info"
                data-place="bottom"
                data-tip={`<p>Prix de vente/place : Prix auquel la place de cinéma sera vendue</p>`}
                id="price-tooltip"
              >
                <Icon
                  alt="image d’aide à l’information"
                  svg="picto-info"
                />
              </span>
            </div>
            <NumberField
              className={classNames('field-text price-field')}
              name="price"
              placeholder="Ex : 12€"
              required
            />

          </div>
        )}

        { !isLoadingMode && (
          <div className="provider-import-button-container">
            <button
              className="button is-intermediate provider-import-button"
              onClick={this.handleShowModal}
              type="button"
            >
              {'Importer'}
            </button>
          </div>
        )}
      </div>
    )
  }

  render() {
    const {isShowingConfirmationModal} = this.state
    return (
      <React.Fragment>
        <Form
          onSubmit={this.handleSubmit}
          render={this.renderForm}
        />

        {isShowingConfirmationModal && (
          <SynchronisationConfirmationModal
            handleClose={this.hideModal}
            handleConfirm={this.handleSubmit}
          />
        )}
      </React.Fragment>
    )
  }
}


AllocineProviderForm.propTypes = {
  history: PropTypes.shape().isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape(),
  }).isRequired,
  notify: PropTypes.func.isRequired,
  venueIdAtOfferProviderIsRequired: PropTypes.bool.isRequired,
}

export default AllocineProviderForm
