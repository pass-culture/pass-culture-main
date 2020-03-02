import classNames from 'classnames'
import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import NumberField from '../../../../layout/form/fields/NumberField'
import Icon from '../../../../layout/Icon'
import { Form } from 'react-final-form'
import SynchronisationConfirmationModal from './SynchronisationConfirmationModal/SynchronisationConfirmationModal'
import { getCanSubmit } from 'react-final-form-utils'
import Insert from "../../../../layout/Insert/Insert"
import CheckboxField from "../../../../layout/form/fields/CheckboxField"

class AllocineProviderForm extends PureComponent {
  constructor() {
    super()
    this.state = {
      isLoadingMode: false,
      isShowingConfirmationModal: false,
    }
  }

  handleSubmit = (formValues) => {
    this.hideModal()
    const { createVenueProvider, providerId, venueId } = this.props
    const { available, isDuo, price } = formValues

    const payload = {
      available,
      isDuo,
      price,
      providerId,
      venueId,
    }

    this.setState({ isLoadingMode: true })

    createVenueProvider(this.handleFail, this.handleSuccess, payload)
  }

  handleSuccess = () => {
    const {
      history,
      offererId,
      venueId
    } = this.props

    history.push(`/structures/${offererId}/lieux/${venueId}`)
  }

  handleFail = () => (state, action) => {
    this.setState({ isLoadingMode: false })
    const { notify } = this.props
    const {
      payload: { errors },
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

  renderForm = (formProps) => {
    const { isLoadingMode, isShowingConfirmationModal } = this.state
    const required = value => {
      return value ? undefined : 'Ce champ est obligatoire'
    }

    const canSubmit = getCanSubmit(formProps)

    return (
      <form onSubmit={formProps.handleSubmit}>
        {!isLoadingMode && (
          <div className="allocine-provider-form">
            <div className="apf-price-section">
              <div className="price-section-label">
                <label
                  htmlFor="price"
                >
                  {'Prix de vente/place '}
                  <span className="field-asterisk">
                    {'*'}
                  </span>
                </label>
                <span
                  className="apf-tooltip"
                  data-place="bottom"
                  data-tip="<p>Prix de vente/place : Prix auquel la place de cinéma sera vendue.</p>"
                  data-type="info"
                >
                  <Icon
                    svg="picto-info"
                  />
                </span>
              </div>
              <NumberField
                className={classNames('field-text price-field')}
                min="0"
                name="price"
                placeholder="Ex : 12€"
                validate={required}
              />
            </div>
            <div className="apf-available-section">
              <label
                className="label-available"
                htmlFor="available"
              >
                {'Nombre de places/séance'}
              </label>
              <NumberField
                min="0"
                name="available"
                placeholder="Illimité"
              />
            </div>
            <div className="apf-is-duo-section">
              <CheckboxField
                id="apf-is-duo"
                label="Accepter les réservations DUO"
                name="isDuo"
              />
              <span
                className="apf-tooltip"
                data-place="bottom"
                data-tip="<p>En activant cette option, vous permettez au bénéficiaire du pass Culture de venir accompagné. La seconde place sera délivrée au même tarif que la première, quel que soit l’accompagnateur.</p>"
                data-type="info"
              >
                <Icon
                  svg="picto-info"
                />
              </span>
            </div>

            <Insert
              className='blue-insert'
              icon='picto-info-solid-black'
            >
              {'Pour le moment, seules les séances "classiques" peuvent être importées.'}
              <p />
              {'Les séances spécifiques (3D, Dolby Atmos, 4DX...) ne génèreront pas d\'offres.'}
              <p />
              {'Nous travaillons actuellement à l\'ajout de séances spécifiques.'}
            </Insert>

            <div className="apf-provider-import-button-section">
              <button
                className="button is-primary apf-provider-import-button"
                disabled={!canSubmit}
                onClick={this.handleShowModal}
                type="button"
              >
                {'Importer les offres'}
              </button>
            </div>
          </div>
        )}

        {isShowingConfirmationModal && (
          <SynchronisationConfirmationModal
            handleClose={this.hideModal}
            handleConfirm={formProps.handleSubmit}
          />
        )}
      </form>
    )
  }

  render() {
    return (
      <Form
        onSubmit={this.handleSubmit}
        render={this.renderForm}
      />
    )
  }
}


AllocineProviderForm.propTypes = {
  history: PropTypes.shape().isRequired,
  notify: PropTypes.func.isRequired,
  providerId: PropTypes.string.isRequired,
  venueId: PropTypes.string.isRequired,
}

export default AllocineProviderForm
