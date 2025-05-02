import * as Dialog from '@radix-ui/react-dialog'
import { useForm } from 'react-hook-form'

import { PostVenueProviderBody } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { SynchronizationEvents } from 'commons/core/FirebaseEvents/constants'
import { FormLayout } from 'components/FormLayout/FormLayout'
import strokeDuoIcon from 'icons/stroke-duo.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import {
  BaseCheckbox,
  CheckboxVariant,
} from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { QuantityInput } from 'ui-kit/formV2/QuantityInput/QuantityInput'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import styles from './AllocineProviderForm.module.scss'

export interface FormValuesProps {
  isDuo: boolean
  price: number | string
  quantity: number | string
  isActive?: boolean
}

export interface AllocineProviderFormProps {
  saveVenueProvider: (payload: PostVenueProviderBody) => Promise<boolean>
  providerId: number
  offererId: number
  venueId: number
  isCreatedEntity?: boolean
  initialValues?: FormValuesProps
}

export const AllocineProviderForm = ({
  saveVenueProvider,
  providerId,
  offererId,
  venueId,
  initialValues = {
    isDuo: false,
    quantity: '',
    price: '',
    isActive: false,
  },
  isCreatedEntity = false,
}: AllocineProviderFormProps): JSX.Element => {
  const { logEvent } = useAnalytics()

  const onSubmit = async (formValues: FormValuesProps) => {
    const { isDuo = true } = formValues
    const quantity =
      formValues.quantity !== '' ? Number(formValues.quantity) : undefined

    const payload = {
      quantity,
      isDuo,
      price: Number(formValues.price),
      providerId,
      venueId,
      isActive: initialValues.isActive,
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
    defaultValues: initialValues,
    // resolver: yupResolver(validationSchema),
  })

  const {
    register,
    handleSubmit,
    watch,
    formState: { isValid, isDirty, isSubmitting },
  } = hookForm

  const isDuo = watch('isDuo')

  return (
    <form
      className={styles['form-content']}
      data-testid="allocine-provider-form"
      onSubmit={(e) => {
        //  avoid submitting parent form
        e.stopPropagation()
        e.preventDefault()
        return handleSubmit(onSubmit)(e)
      }}
    >
      <FormLayout.Row className={styles['form-layout-row']}>
        <TextInput
          {...register('price')}
          type="number"
          label="Prix de vente/place"
          min="0"
          description="Le prix doit être indiqué en euros."
          step={0.01}
          className={styles['price-input']}
          required
        />
        <QuantityInput
          label="Nombre de places/séance"
          className={styles['nb-places-input']}
          min={'1'}
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <BaseCheckbox
          {...register('isDuo')}
          label="Accepter les réservations duo"
          description="Cette option permet au bénéficiaire du pass Culture de venir accompagné. La seconde place sera délivrée au même tarif que la première, quel que soit l’accompagnateur."
          hasError={isDirty && !isValid}
          variant={CheckboxVariant.BOX}
          icon={strokeDuoIcon}
          checked={isDuo}
        />
      </FormLayout.Row>
      <Callout className={styles['allocine-provider-form-banner']}>
        Pour le moment, seules les séances "classiques" peuvent être importées.
        Les séances spécifiques (3D, Dolby Atmos, 4DX...) ne génèreront pas
        d’offres. Nous travaillons actuellement à l’ajout de séances
        spécifiques.
      </Callout>
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
          <div className={styles['allocine-provider-form-actions']}>
            <Dialog.Close asChild>
              <Button variant={ButtonVariant.SECONDARY} type="button">
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
