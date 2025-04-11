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
import { CheckboxVariant } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { Checkbox } from 'ui-kit/formV2/Checkbox/Checkbox'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

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

  const hookForm = useForm<CinemaProviderFormValues>({
    defaultValues: initialValues ?? DEFAULT_CINEMA_PROVIDER_FORM_VALUES,
    mode: 'onBlur',
  })

  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
    getValues,
  } = hookForm

  // Submit form handler
  const onsubmit = async () => {
    const payload = {
      providerId,
      venueId,
      isDuo: getValues('isDuo'),
      isActive: getValues('isActive'),
    }

    const isSuccess = await saveVenueProvider(payload)

    logEvent(SynchronizationEvents.CLICKED_IMPORT, {
      offererId,
      venueId,
      providerId,
      saved: isSuccess,
    })
  }

  return (
    <form
      className={styles['cinema-provider-form']}
      data-testid="cinema-provider-form"
      onSubmit={handleSubmit(onsubmit)}
    >
      {!isSubmitting && (
        <>
          <FormLayout.Row className={styles['cinema-provider-form-content']}>
            <Checkbox
              label="Accepter les réservations “Duo“"
              description="Cette option permet au bénéficiaire du pass Culture de venir accompagné. La seconde place sera délivrée au même tarif que la première, quel que soit l’accompagnateur."
              variant={CheckboxVariant.BOX}
              {...register('isDuo')}
            />
            <SvgIcon
              className={styles['duo-checkbox-icon']}
              src={strokeDuoIcon}
              alt="Duo"
              width="40"
            />
          </FormLayout.Row>

          <DialogBuilder.Footer>
            {isCreatedEntity ? (
              <Button
                type="button"
                variant={ButtonVariant.PRIMARY}
                isLoading={isSubmitting}
                onClick={onsubmit}
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
                    onClick={onsubmit}
                  >
                    Modifier
                  </Button>
                </Dialog.Close>
              </div>
            )}
          </DialogBuilder.Footer>
        </>
      )}
    </form>
  )
}
