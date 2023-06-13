import React, { useCallback, useState } from 'react'
import { Form } from 'react-final-form'
import type { FormRenderProps } from 'react-final-form'
import { Tooltip } from 'react-tooltip'

import { SynchronizationEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { Banner, Button, SubmitButton, CheckboxField } from 'ui-kit'
import 'react-tooltip/dist/react-tooltip.css'
import { ButtonVariant } from 'ui-kit/Button/types'
import NumberField from 'ui-kit/form_rff/fields/NumberField'
import Icon from 'ui-kit/Icon/Icon'
import { getCanSubmit } from 'utils/react-final-form'
import './AllocineProviderForm.scss'

interface FormProps {
  isLoading: boolean
  dirtySinceLastSubmit: boolean
  hasSubmitErrors: boolean
  hasValidationErrors: boolean
  pristine: boolean
  handleSubmit: () => void
}

interface FormValuesProps {
  isDuo: boolean
  price?: number
  quantity: string | number | null
  isActive?: boolean
}
export type InitialValuesProps = FormProps & FormValuesProps

export interface AllocineProviderFormProps {
  saveVenueProvider: (payload?: FormValuesProps) => void
  providerId: number
  offererId: number
  venueId: number
  isCreatedEntity?: boolean
  onCancel: () => void
  initialValues: InitialValuesProps
}

const AllocineProviderForm = ({
  saveVenueProvider,
  providerId,
  offererId,
  venueId,
  onCancel,
  initialValues,
  isCreatedEntity = false,
}: AllocineProviderFormProps): JSX.Element => {
  const [isLoading, setIsLoading] = useState(false)
  const { logEvent } = useAnalytics()

  const handleSubmit = (formValues: FormValuesProps) => {
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
    logEvent?.(SynchronizationEvents.CLICKED_IMPORT, {
      offererId: offererId,
      venueId: venueId,
      providerId: providerId,
    })
  }

  const required = (value: number | undefined) => {
    return typeof value === 'number' ? undefined : 'Ce champ est obligatoire'
  }

  const renderForm = useCallback(
    (
      formProps: FormRenderProps<FormValuesProps, FormProps>
    ): React.ReactNode => {
      const canSubmit = getCanSubmit({
        isLoading: isLoading,
        dirtySinceLastSubmit: formProps.dirtySinceLastSubmit,
        hasSubmitErrors: formProps.hasSubmitErrors,
        hasValidationErrors: formProps.hasValidationErrors,
        pristine: formProps.pristine,
      })
      return (
        <form className="allocine-provider-form">
          {!isLoading && (
            <div className="allocine-provider-content">
              <div className="apf-price-section">
                <div className="price-section-label">
                  <label htmlFor="price">
                    Prix de vente/place{' '}
                    <span className="field-asterisk">*</span>
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
                  </label>
                </div>
                <NumberField
                  onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) =>
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
                  className="quantity-field"
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
              </div>
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

              <Banner type="notification-info">
                <p>
                  Pour le moment, seules les séances "classiques" peuvent être
                  importées.
                </p>
                <p>
                  Les séances spécifiques (3D, Dolby Atmos, 4DX...) ne
                  génèreront pas d’offres.
                </p>
                <p>
                  Nous travaillons actuellement à l’ajout de séances
                  spécifiques.
                </p>
              </Banner>
              {isCreatedEntity ? (
                <div className="apf-provider-import-button-section">
                  <SubmitButton
                    variant={ButtonVariant.PRIMARY}
                    disabled={!canSubmit}
                    onClick={formProps.handleSubmit}
                  >
                    Importer les offres
                  </SubmitButton>
                </div>
              ) : (
                <div className="actions">
                  <Button
                    variant={ButtonVariant.SECONDARY}
                    onClick={onCancel}
                    type="button"
                  >
                    Annuler
                  </Button>
                  <SubmitButton
                    variant={ButtonVariant.PRIMARY}
                    disabled={!canSubmit}
                    onClick={formProps.handleSubmit}
                  >
                    Modifier
                  </SubmitButton>
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

export default AllocineProviderForm
