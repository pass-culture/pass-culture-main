import * as Dialog from '@radix-ui/react-dialog'
import { useState } from 'react'
import { Controller, useForm } from 'react-hook-form'

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

  // React Hook Form setup
  const form = useForm<CinemaProviderFormValues>({
    defaultValues: initialValues
      ? initialValues
      : DEFAULT_CINEMA_PROVIDER_FORM_VALUES,
  })

  const {
    handleSubmit,
    control,
    formState: { isSubmitting },
  } = form

  const handleFormSubmit = async (values: CinemaProviderFormValues) => {
    const payload = {
      providerId,
      venueId,
      isDuo: values.isDuo,
      isActive: initialValues?.isActive,
    }

    setIsLoading(true)

    const isSuccess = await saveVenueProvider(payload)
    logEvent(SynchronizationEvents.CLICKED_IMPORT, {
      offererId,
      venueId,
      providerId,
      saved: isSuccess,
    })
  }

  return (
    <>
      {!isLoading && (
        <form
          className={styles['cinema-provider-form']}
          data-testid="cinema-provider-form"
        >
          <FormLayout.Row className={styles['cinema-provider-form-content']}>
            {/* Using Controller to manage custom inputs */}
            <Controller
              name="isDuo"
              control={control}
              render={({ field }) => <DuoCheckbox {...field} />}
            />
          </FormLayout.Row>

          <DialogBuilder.Footer>
            {isCreatedEntity ? (
              <Button
                type="button"
                variant={ButtonVariant.PRIMARY}
                isLoading={isSubmitting}
                onClick={() => handleFormSubmit(form.getValues())}
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
                    isLoading={isSubmitting}
                    onClick={() => handleFormSubmit(form.getValues())}
                  >
                    Modifier
                  </Button>
                </Dialog.Close>
              </div>
            )}
          </DialogBuilder.Footer>
        </form>
      )}
    </>
  )
}
