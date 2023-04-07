import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'
import { Form } from 'react-final-form'
import { Tooltip } from 'react-tooltip'

import 'react-tooltip/dist/react-tooltip.css'
import { CheckboxField } from 'ui-kit'
import NumberField from 'ui-kit/form_rff/fields/NumberField'
import Icon from 'ui-kit/Icon/Icon'
import Insert from 'ui-kit/Insert/Insert'
import { getCanSubmit } from 'utils/react-final-form'
const AllocineProviderForm = ({
  saveVenueProvider,
  providerId,
  venueId,
  isCreatedEntity,
  initialValues,
  onCancel,
}) => {
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = useCallback(
    formValues => {
      const { isDuo = true, price } = formValues
      const quantity = formValues.quantity !== '' ? formValues.quantity : null

      const payload = {
        quantity,
        isDuo,
        price,
        providerId,
        venueId,
        isActive: initialValues.isActive,
      }

      setIsLoading(true)

      saveVenueProvider(payload)
    },
    [saveVenueProvider, providerId, venueId]
  )

  const required = useCallback(value => {
    return typeof value === 'number' ? undefined : 'Ce champ est obligatoire'
  }, [])

  const renderForm = useCallback(
    formProps => {
      const canSubmit = getCanSubmit({
        isLoading: formProps.isLoading,
        dirtySinceLastSubmit: formProps.dirtySinceLastSubmit,
        hasSubmitErrors: formProps.hasSubmitErrors,
        hasValidationErrors: formProps.hasValidationErrors,
        pristine: formProps.pristine,
      })
      return (
        <form>
          {!isLoading && (
            <div className="allocine-provider-form">
              <div className="apf-price-section">
                <div className="price-section-label">
                  <label htmlFor="price">
                    Prix de vente/place{' '}
                    <span className="field-asterisk">*</span>
                  </label>
                  <span
                    className="apf-tooltip"
                    data-tooltip-place="bottom"
                    data-tooltip-html="<p>Prix de vente/place : Prix auquel la place de cinéma sera vendue.</p>"
                    data-tooltip-id="tooltip-price"
                    data-type="info"
                  >
                    <Icon svg="picto-info" />
                  </span>
                  <Tooltip
                    className="type-info flex-center items-center"
                    delayHide={500}
                    id="tooltip-price"
                  />
                </div>
                <NumberField
                  onKeyPress={e =>
                    (e.key === 'e' || e.key === 'E') && e.preventDefault()
                  }
                  className="field-text price-field"
                  min="0"
                  name="price"
                  placeholder="Ex : 12€"
                  step={0.01}
                  validate={required}
                />
              </div>
              <div className="apf-quantity-section">
                <label className="label-quantity" htmlFor="quantity">
                  Nombre de places/séance
                </label>
                <NumberField
                  isDecimal={false}
                  min="0"
                  name="quantity"
                  placeholder="Illimité"
                  step={1}
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
                  data-tooltip-place="bottom"
                  data-tooltip-html="<p>En activant cette option, vous permettez au bénéficiaire du pass Culture de venir accompagné. La seconde place sera délivrée au même tarif que la première, quel que soit l’accompagnateur.</p>"
                  data-tooltip-type="info"
                  data-tooltip-id="tooltip-duo"
                >
                  <Icon svg="picto-info" />
                </span>
                <Tooltip
                  className="type-info flex-center items-center"
                  delayHide={500}
                  id="tooltip-duo"
                />
              </div>

              <Insert className="blue-insert" icon="picto-info-solid-black">
                Pour le moment, seules les séances &quot;classiques&quot;
                peuvent être importées.
                <br />
                Les séances spécifiques (3D, Dolby Atmos, 4DX...) ne génèreront
                pas d’offres.
                <br />
                Nous travaillons actuellement à l’ajout de séances spécifiques.
              </Insert>
              {isCreatedEntity ? (
                <div className="apf-provider-import-button-section">
                  <button
                    className="primary-button"
                    disabled={!canSubmit}
                    onClick={formProps.handleSubmit}
                    type="submit"
                  >
                    Importer les offres
                  </button>
                </div>
              ) : (
                <div className="actions">
                  <button
                    className="secondary-button"
                    onClick={onCancel}
                    type="button"
                  >
                    Annuler
                  </button>
                  <button
                    className="primary-button"
                    disabled={!canSubmit}
                    onClick={formProps.handleSubmit}
                    type="submit"
                  >
                    Modifier
                  </button>
                </div>
              )}
            </div>
          )}
        </form>
      )
    },
    [isCreatedEntity, isLoading, onCancel, required]
  )

  return (
    <Form
      initialValues={initialValues}
      onSubmit={handleSubmit}
      render={renderForm}
    />
  )
}

AllocineProviderForm.defaultProps = {
  initialValues: {
    isDuo: true,
  },
  isCreatedEntity: false,
  onCancel: () => {},
}

AllocineProviderForm.propTypes = {
  initialValues: PropTypes.shape({
    isDuo: PropTypes.bool,
    price: PropTypes.number,
    quantity: PropTypes.number,
  }),
  isCreatedEntity: PropTypes.bool,
  onCancel: PropTypes.func,
  providerId: PropTypes.number.isRequired,
  saveVenueProvider: PropTypes.func.isRequired,
  venueId: PropTypes.number.isRequired,
}

export default AllocineProviderForm
