import * as Dialog from '@radix-ui/react-dialog'
import { useState } from 'react'
import { Controller, useForm } from 'react-hook-form'

import { PostVenueProviderBody } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { SynchronizationEvents } from 'commons/core/FirebaseEvents/constants'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { validationSchema } from 'pages/VenueSettings/VenueProvidersManager/AllocineProviderForm/validationSchema'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { QuantityInput } from 'ui-kit/form/QuantityInput/QuantityInput'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import { DuoCheckbox } from '../DuoCheckbox/DuoCheckbox'

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
  const [isLoading, setIsLoading] = useState(false)
  const { logEvent } = useAnalytics()

  // React Hook Form setup
  const form = useForm<FormValuesProps>({
    defaultValues: initialValues,
    resolver: async (data) => {
      // Using validation schema here
      try {
        await validationSchema.validate(data, { abortEarly: false })
        return { values: data, errors: {} }
      } catch (err) {
        return {
          values: {},
          errors: err.inner.reduce((acc: any, curr: any) => {
            acc[curr.path] = { message: curr.message }
            return acc
          }, {}),
        }
      }
    },
  })

  const {
    handleSubmit,
    control,
    formState: { isSubmitting, isValid, errors },
  } = form

  const handleFormSubmit = async (formValues: FormValuesProps) => {
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

    setIsLoading(true)

    const isSuccess = await saveVenueProvider(payload)

    setIsLoading(false)

    logEvent(SynchronizationEvents.CLICKED_IMPORT, {
      offererId: offererId,
      venueId: venueId,
      providerId: providerId,
      saved: isSuccess,
    })
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)}>
      <div
        className={styles['form-content']}
        data-testid="allocine-provider-form"
      >
        <FormLayout.Row className={styles['form-layout-row']}>
          <Controller
            name="price"
            control={control}
            render={({ field }) => (
              <TextInput
                {...field}
                type="number"
                label="Prix de vente/place"
                min="0"
                description="Le prix doit être indiqué en euros."
                step={0.01}
                className={styles['price-input']}
                required
              />
            )}
          />
          <Controller
            name="quantity"
            control={control}
            render={({ field }) => (
              <QuantityInput
                {...field}
                label="Nombre de places/séance"
                className={styles['nb-places-input']}
                isOptional
                min={1}
              />
            )}
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <Controller
            name="isDuo"
            control={control}
            render={({ field }) => <DuoCheckbox {...field} />}
          />
        </FormLayout.Row>
        <Callout className={styles['allocine-provider-form-banner']}>
          Pour le moment, seules les séances "classiques" peuvent être
          importées. Les séances spécifiques (3D, Dolby Atmos, 4DX...) ne
          génèreront pas d’offres. Nous travaillons actuellement à l’ajout de
          séances spécifiques.
        </Callout>
      </div>
      <DialogBuilder.Footer>
        <div className={styles['allocine-provider-form-actions']}>
          {!isCreatedEntity ? (
            <Dialog.Close asChild>
              <Button variant={ButtonVariant.SECONDARY} type="button">
                Annuler
              </Button>
            </Dialog.Close>
          ) : (
            <></>
          )}

          <Dialog.Close asChild>
            <Button
              type="button"
              isLoading={isSubmitting}
              disabled={!isValid || !errors}
              onClick={() => handleFormSubmit(form.getValues())}
            >
              {isCreatedEntity ? 'Lancer la synchronisation' : 'Modifier'}
            </Button>
          </Dialog.Close>
        </div>
      </DialogBuilder.Footer>
    </form>
  )
}
