import './CinemaProviderForm.scss'

import { Checkbox, SubmitButton } from 'ui-kit'
import { Form, FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'
import { DEFAULT_CINEMA_PROVIDER_FORM_VALUES } from './constants'
import FormLayout from 'new_components/FormLayout'
import { ICinemaProviderFormValues } from './types'
import Icon from 'components/layout/Icon'
import ReactTooltip from 'react-tooltip'

interface ICinemaProviderFormProps {
  saveVenueProvider: (values: ICinemaProviderFormValues) => void
  providerId: string
  venueId: string
  isCreatedEntity?: boolean
  initialValues?: ICinemaProviderFormValues
  onCancel?: () => void
}

export const CinemaProviderForm = ({
  saveVenueProvider,
  providerId,
  venueId,
  isCreatedEntity = false,
  initialValues,
  onCancel,
}: ICinemaProviderFormProps): JSX.Element => {
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    ReactTooltip.rebuild()
  }, [])

  const handleFromSubmit = (values: ICinemaProviderFormValues) => {
    const payload = {
      providerId,
      venueId,
      isDuo: values.isDuo,
      isActive: values.isActive,
    }

    setIsLoading(true)

    saveVenueProvider(payload)
  }
  const formik = useFormik({
    initialValues: initialValues
      ? initialValues
      : DEFAULT_CINEMA_PROVIDER_FORM_VALUES,
    onSubmit: handleFromSubmit,
  })

  return (
    <FormikProvider value={formik}>
      <Form onSubmit={formik.handleSubmit}>
        <FormLayout>
          {!isLoading && (
            <div className="cinema-provider-form">
              <FormLayout.Row inline>
                <Checkbox
                  className="cpf-is-duo"
                  label="Accepter les réservations DUO"
                  name="isDuo"
                  // @ts-ignore
                  value={formik.values.isDuo}
                />
                <span
                  className="cpf-tooltip"
                  data-place="bottom"
                  data-tip="<p>En activant cette option, vous permettez au bénéficiaire du pass Culture de venir accompagné. La seconde place sera délivrée au même tarif que la première, quel que soit l’accompagnateur.</p>"
                  data-type="info"
                >
                  <Icon svg="picto-info" />
                </span>
              </FormLayout.Row>
              {isCreatedEntity ? (
                <div className="cpf-provider-import-button">
                  <SubmitButton
                    className="primary-button"
                    isLoading={formik.isSubmitting}
                  >
                    Importer les offres
                  </SubmitButton>
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
                  <SubmitButton
                    className="primary-button"
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
