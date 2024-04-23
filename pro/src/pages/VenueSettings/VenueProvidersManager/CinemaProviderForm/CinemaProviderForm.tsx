import { Form, FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'

import { PostVenueProviderBody } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { SynchronizationEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { Checkbox, InfoBox } from 'ui-kit'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SubmitButton } from 'ui-kit/SubmitButton/SubmitButton'

import styles from './CinemaProviderForm.module.scss'
import { DEFAULT_CINEMA_PROVIDER_FORM_VALUES } from './constants'
import { CinemaProviderFormValues } from './types'

export interface CinemaProviderFormProps {
  saveVenueProvider: (values: PostVenueProviderBody) => Promise<boolean>
  providerId: number
  venueId: number
  offererId: number
  isCreatedEntity?: boolean
  initialValues?: CinemaProviderFormValues
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
}: CinemaProviderFormProps): JSX.Element => {
  const [isLoading, setIsLoading] = useState(false)
  const { logEvent } = useAnalytics()

  const handleFormSubmit = async (values: CinemaProviderFormValues) => {
    const payload = {
      providerId,
      venueId,
      isDuo: values.isDuo,
      isActive: values.isActive,
    }

    setIsLoading(true)

    const isSuccess = await saveVenueProvider(payload)
    logEvent?.(SynchronizationEvents.CLICKED_IMPORT, {
      offererId: offererId,
      venueId: venueId,
      providerId: providerId,
      saved: isSuccess,
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
            <div className={styles['cinema-provider-form']}>
              <FormLayout.Row
                inline
                sideComponent={
                  isCreatedEntity ? (
                    <InfoBox>
                      En activant cette option, vous permettez au bénéficiaire
                      du pass Culture de venir accompagné. La seconde place sera
                      délivrée au même tarif que la première, quel que soit
                      l’accompagnateur.
                    </InfoBox>
                  ) : (
                    <></>
                  )
                }
              >
                <Checkbox name="isDuo" label="Accepter les réservations DUO" />
              </FormLayout.Row>

              {isCreatedEntity ? (
                <SubmitButton
                  variant={ButtonVariant.PRIMARY}
                  isLoading={formik.isSubmitting}
                >
                  Lancer la synchronisation
                </SubmitButton>
              ) : (
                <div>
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
