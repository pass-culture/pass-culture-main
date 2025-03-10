import * as Dialog from '@radix-ui/react-dialog'
import { Form, FormikProvider, useFormik } from 'formik'
import { useState } from 'react'

import { PostVenueProviderBody } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { SynchronizationEvents } from 'commons/core/FirebaseEvents/constants'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'

import { DuoCheckbox } from '../DuoCheckbox/DuoCheckbox'

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
      {!isLoading && (
        <Form className={styles['cinema-provider-form']}>
          <FormLayout.Row className={styles['cinema-provider-form-content']}>
            <DuoCheckbox isChecked={formik.values.isDuo} />
          </FormLayout.Row>

          <DialogBuilder.Footer>
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
              <div className={styles['cinema-provider-form-buttons']}>
                <Dialog.Close asChild>
                  <Button
                    variant={ButtonVariant.SECONDARY}
                    onClick={onCancel}
                    type="button"
                  >
                    Annuler
                  </Button>
                </Dialog.Close>
                <Dialog.Close asChild>
                  <Button
                    type="submit"
                    variant={ButtonVariant.PRIMARY}
                    isLoading={formik.isSubmitting}
                  >
                    Modifier
                  </Button>
                </Dialog.Close>
              </div>
            )}
          </DialogBuilder.Footer>
        </Form>
      )}
    </FormikProvider>
  )
}
