import * as Dialog from '@radix-ui/react-dialog'
import { useForm } from 'react-hook-form'

import { PostVenueProviderBody } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { SynchronizationEvents } from 'commons/core/FirebaseEvents/constants'
import { DuoCheckbox } from 'components/DuoCheckbox/DuoCheckbox'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { QuantityInput } from 'ui-kit/formV2/QuantityInput/QuantityInput'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import styles from './GenericCinemaProviderForm.module.scss'
export interface GenericCinemaProviderFormValues {
  isDuo: boolean
  price?: number | null
  quantity?: number | null
  isActive?: boolean
}

export interface GenericCinemaProviderFormProps {
  saveVenueProvider: (payload: PostVenueProviderBody) => Promise<boolean>
  providerId: number
  venueId: number
  offererId: number
  isCreatedEntity?: boolean
  initialValues?: GenericCinemaProviderFormValues
  onCancel?: () => void
  showAdvancedFields?: boolean // If true, show price & quantity
}

export const GenericCinemaProviderForm = ({
  saveVenueProvider,
  providerId,
  venueId,
  offererId,
  isCreatedEntity = false,
  initialValues,
  onCancel,
  showAdvancedFields = false,
}: GenericCinemaProviderFormProps): JSX.Element => {
  const { logEvent } = useAnalytics()

  const onSubmit = async (formValues: GenericCinemaProviderFormValues) => {
    const payload: PostVenueProviderBody = {
      providerId,
      venueId,
      isDuo: formValues.isDuo,
      isActive: formValues.isActive,
    }

    if (showAdvancedFields) {
      payload.price = Number(formValues.price)
      payload.quantity = formValues.quantity
        ? Number(formValues.quantity)
        : undefined
    }

    const isSuccess = await saveVenueProvider(payload)

    logEvent(SynchronizationEvents.CLICKED_IMPORT, {
      offererId,
      venueId,
      providerId,
      saved: isSuccess,
    })
  }

  const hookForm = useForm({
    defaultValues: initialValues,
    mode: 'onChange',
  })

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { isValid, isSubmitting },
  } = hookForm

  const formValues = watch()

  return (
    <form
      className={styles['cinema-provider-form']}
      data-testid="generic-cinema-provider-form"
      onSubmit={(e) => {
        e.stopPropagation()
        e.preventDefault()
        return handleSubmit(onSubmit)(e)
      }}
    >
      <div className={styles['cinema-provider-form-content']}>
        {showAdvancedFields && (
          <FormLayout.Row className={styles['form-layout-row']}>
            <TextInput
              {...register('price', {
                required: 'Veuillez renseigner un prix de vente',
              })}
              type="number"
              label="Prix de vente/place"
              min="1"
              description="Le prix doit être indiqué en euros."
              step={0.01}
              className={styles['price-input']}
              required
            />
            <QuantityInput
              minimum={1}
              label="Nombre de places/séance"
              className={styles['nb-places-input']}
              value={formValues.quantity ?? undefined}
              onChange={(e) => setValue('quantity', Number(e.target.value))}
            />
          </FormLayout.Row>
        )}

        <FormLayout.Row>
          <DuoCheckbox
            {...register('isDuo')}
            checked={Boolean(watch('isDuo'))}
          />
        </FormLayout.Row>

        {showAdvancedFields && (
          <Callout className={styles['allocine-provider-form-banner']}>
            Pour le moment, seules les séances "classiques" peuvent être
            importées. Les séances spécifiques (3D, Dolby Atmos, 4DX...) ne
            génèreront pas d’offres. Nous travaillons actuellement à l’ajout de
            séances spécifiques.
          </Callout>
        )}
      </div>

      <DialogBuilder.Footer>
        {isCreatedEntity ? (
          <Button
            type="submit"
            variant={ButtonVariant.PRIMARY}
            isLoading={isSubmitting}
            disabled={!isValid}
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
              disabled={!isValid}
            >
              Modifier
            </Button>
          </div>
        )}
      </DialogBuilder.Footer>
    </form>
  )
}
