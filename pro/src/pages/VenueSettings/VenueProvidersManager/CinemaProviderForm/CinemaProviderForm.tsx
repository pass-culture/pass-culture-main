import { Form, FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'

import { PostVenueProviderBody } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { SynchronizationEvents } from 'core/FirebaseEvents/constants'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Checkbox } from 'ui-kit/form/Checkbox/Checkbox'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

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
    logEvent(SynchronizationEvents.CLICKED_IMPORT, {
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
                <Button
                  type="button"
                  variant={ButtonVariant.PRIMARY}
                  isLoading={formik.isSubmitting}
                  onClick={() => handleFormSubmit(formik.values)}
                >
                  Lancer la synchronisation
                </Button>
              ) : (
                <div>
                  <Button
                    variant={ButtonVariant.SECONDARY}
                    onClick={onCancel}
                    type="button"
                  >
                    Annuler
                  </Button>
                  <Button
                    type="submit"
                    variant={ButtonVariant.PRIMARY}
                    isLoading={formik.isSubmitting}
                  >
                    Modifier
                  </Button>
                </div>
              )}
            </div>
          )}
        </FormLayout>
      </Form>
    </FormikProvider>
  )
}
