import './CinemaProviderForm.scss'

import { Form, FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'
import { Tooltip } from 'react-tooltip'

import 'react-tooltip/dist/react-tooltip.css'
import FormLayout from 'components/FormLayout'
import { SynchronizationEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { Button, Checkbox, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Icon from 'ui-kit/Icon/Icon'

import { DEFAULT_CINEMA_PROVIDER_FORM_VALUES } from './constants'
import { ICinemaProviderFormValues } from './types'

export interface ICinemaProviderFormProps {
  saveVenueProvider: (values: ICinemaProviderFormValues) => void
  providerId: number
  venueId: number
  offererId: number
  isCreatedEntity?: boolean
  initialValues: ICinemaProviderFormValues
  onCancel?: () => void
}

export const CinemaProviderForm = ({
  saveVenueProvider,
  providerId,
  venueId,
  offererId,
  isCreatedEntity = false,
  initialValues,
  onCancel,
}: ICinemaProviderFormProps): JSX.Element => {
  const [isLoading, setIsLoading] = useState(false)
  const { logEvent } = useAnalytics()

  const handleFormSubmit = (values: ICinemaProviderFormValues) => {
    const payload = {
      providerId,
      venueId,
      isDuo: values.isDuo,
      isActive: values.isActive,
    }

    setIsLoading(true)

    saveVenueProvider(payload)
    logEvent?.(SynchronizationEvents.CLICKED_IMPORT, {
      offererId: offererId,
      venueId: venueId,
      providerId: providerId,
    })
  }
  const formik = useFormik({
    initialValues: initialValues
      ? initialValues
      : DEFAULT_CINEMA_PROVIDER_FORM_VALUES,
    onSubmit: handleFormSubmit,
  })

  return (
    <FormikProvider value={formik}>
      <Form>
        <FormLayout>
          {!isLoading && (
            <div className="cinema-provider-form">
              <FormLayout.Row inline>
                <Checkbox
                  className="cpf-is-duo"
                  label="Accepter les réservations DUO"
                  name="isDuo"
                  // @ts-expect-error
                  value={formik.values.isDuo}
                />
                <span
                  className="cpf-tooltip"
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
              </FormLayout.Row>
              {isCreatedEntity ? (
                <div className="cpf-provider-import-button">
                  <SubmitButton
                    variant={ButtonVariant.PRIMARY}
                    isLoading={formik.isSubmitting}
                    onClick={formik.handleSubmit}
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
                    isLoading={formik.isSubmitting}
                  >
                    Modifier
                  </SubmitButton>
                </div>
              )}
            </div>
          )}
        </FormLayout>
      </Form>
    </FormikProvider>
  )
}
