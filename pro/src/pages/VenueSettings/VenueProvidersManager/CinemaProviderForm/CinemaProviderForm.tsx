import * as Dialog from '@radix-ui/react-dialog'
import { useForm } from 'react-hook-form'

import { PostVenueProviderBody } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { SynchronizationEvents } from 'commons/core/FirebaseEvents/constants'
import { FormLayout } from 'components/FormLayout/FormLayout'
import strokeDuoIcon from 'icons/stroke-duo.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import {
  BaseCheckbox,
  CheckboxVariant,
} from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

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
  const { logEvent } = useAnalytics()

  const onSubmit = async (values: CinemaProviderFormValues) => {
    const payload = {
      providerId,
      venueId,
      isDuo: values.isDuo,
      isActive: values.isActive,
    }

    const isSuccess = await saveVenueProvider(payload)

    logEvent(SynchronizationEvents.CLICKED_IMPORT, {
      offererId: offererId,
      venueId: venueId,
      providerId: providerId,
      saved: isSuccess,
    })
  }

  const hookForm = useForm({
    defaultValues: initialValues
      ? initialValues
      : DEFAULT_CINEMA_PROVIDER_FORM_VALUES,
  })

  const {
    register,
    handleSubmit,
    getValues,
    formState: { isValid, isDirty, isSubmitting },
  } = hookForm

  return (
    <form
      className={styles['cinema-provider-form']}
      data-testid="cinema-provider-form"
      onSubmit={(e) => {
        //  avoid submitting parent form
        e.stopPropagation()
        e.preventDefault()
        return handleSubmit(onSubmit)(e)
      }}
    >
      <FormLayout.Row className={styles['cinema-provider-form-content']}>
        <BaseCheckbox
          {...register('isDuo')}
          label="Accepter les réservations duo"
          description="Cette option permet au bénéficiaire du pass Culture de venir accompagné. La seconde place sera délivrée au même tarif que la première, quel que soit l’accompagnateur."
          hasError={isDirty && !isValid}
          variant={CheckboxVariant.BOX}
          icon={strokeDuoIcon}
          checked={getValues('isDuo')}
        />
      </FormLayout.Row>

      <DialogBuilder.Footer>
        {isCreatedEntity ? (
          <Button
            type="submit"
            variant={ButtonVariant.PRIMARY}
            isLoading={isSubmitting}
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
            <Button
              type="submit"
              variant={ButtonVariant.PRIMARY}
              isLoading={isSubmitting}
            >
              Modifier
            </Button>
          </div>
        )}
      </DialogBuilder.Footer>
    </form>
  )
}
