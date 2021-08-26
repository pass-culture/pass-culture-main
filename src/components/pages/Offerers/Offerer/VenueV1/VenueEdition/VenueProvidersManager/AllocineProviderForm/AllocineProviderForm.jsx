/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt directory "Gaël: this file should be migrated within the new directory structure"
* @debt deprecated "Gaël: deprecated usage of react-final-form"
* @debt deprecated "Gaël: deprecated usage of react-final-form custom fields"
*/

import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'
import { Form } from 'react-final-form'
import { getCanSubmit } from 'react-final-form-utils'

import CheckboxField from 'components/layout/form/fields/CheckboxField'
import NumberField from 'components/layout/form/fields/NumberField'
import Icon from 'components/layout/Icon'
import Insert from 'components/layout/Insert/Insert'

const AllocineProviderForm = ({ createVenueProvider, providerId, venueId }) => {
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = useCallback(
    formValues => {
      const { quantity, isDuo = true, price } = formValues

      const payload = {
        quantity,
        isDuo,
        price,
        providerId,
        venueId,
      }

      setIsLoading(true)

      createVenueProvider(payload)
    },
    [createVenueProvider, providerId, venueId]
  )

  const required = useCallback(value => {
    return typeof value === 'number' ? undefined : 'Ce champ est obligatoire'
  }, [])

  const renderForm = useCallback(
    formProps => {
      const canSubmit = getCanSubmit(formProps)

      return (
        <form>
          {!isLoading && (
            <div className="allocine-provider-form">
              <div className="apf-price-section">
                <div className="price-section-label">
                  <label htmlFor="price">
                    Prix de vente/place 
                    {' '}
                    <span className="field-asterisk">
                      *
                    </span>
                  </label>
                  <span
                    className="apf-tooltip"
                    data-place="bottom"
                    data-tip="<p>Prix de vente/place : Prix auquel la place de cinéma sera vendue.</p>"
                    data-type="info"
                  >
                    <Icon svg="picto-info" />
                  </span>
                </div>
                <NumberField
                  className="field-text price-field"
                  min="0"
                  name="price"
                  placeholder="Ex : 12€"
                  step={0.01}
                  validate={required}
                />
              </div>
              <div className="apf-quantity-section">
                <label
                  className="label-quantity"
                  htmlFor="quantity"
                >
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
                  checked
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
                  <Icon svg="picto-info" />
                </span>
              </div>

              <Insert
                className="blue-insert"
                icon="picto-info-solid-black"
              >
                Pour le moment, seules les séances &quot;classiques&quot; peuvent être importées.
                <br />
                Les séances spécifiques (3D, Dolby Atmos, 4DX...) ne génèreront pas d’offres.
                <br />
                Nous travaillons actuellement à l’ajout de séances spécifiques.
              </Insert>

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
            </div>
          )}
        </form>
      )
    },
    [isLoading, required]
  )

  return (
    <Form
      onSubmit={handleSubmit}
      render={renderForm}
    />
  )
}

AllocineProviderForm.propTypes = {
  createVenueProvider: PropTypes.func.isRequired,
  providerId: PropTypes.string.isRequired,
  venueId: PropTypes.string.isRequired,
}

export default AllocineProviderForm
