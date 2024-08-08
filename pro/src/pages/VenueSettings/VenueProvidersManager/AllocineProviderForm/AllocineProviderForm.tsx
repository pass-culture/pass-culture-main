import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'

import { PostVenueProviderBody } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Callout } from 'components/Callout/Callout'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { SynchronizationEvents } from 'core/FirebaseEvents/constants'
import { validationSchema } from 'pages/VenueSettings/VenueProvidersManager/AllocineProviderForm/validationSchema'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
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
  onCancel?: () => void
  initialValues?: FormValuesProps
}

export const AllocineProviderForm = ({
  saveVenueProvider,
  providerId,
  offererId,
  venueId,
  onCancel,
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

  const handleSubmit = async (formValues: FormValuesProps) => {
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
    logEvent(SynchronizationEvents.CLICKED_IMPORT, {
      offererId: offererId,
      venueId: venueId,
      providerId: providerId,
      saved: isSuccess,
    })
  }

  const formik = useFormik({
    initialValues,
    onSubmit: handleSubmit,
    validationSchema,
  })

  return (
    <FormikProvider value={formik}>
      {!isLoading && (
        <>
          <FormLayout.Row>
            <TextInput
              name="price"
              type="number"
              label="Prix de vente/place"
              min="0"
              description="Le prix doit être indiqué en euros."
              step={0.01}
              className={styles['price-input']}
              required
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <TextInput
              type="number"
              label="Nombre de places/séance"
              min="0"
              name="quantity"
              placeholder="Illimité"
              step={1}
              isOptional
              hasDecimal={false}
              className={styles['nb-places-input']}
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <DuoCheckbox isChecked={formik.values.isDuo} />
          </FormLayout.Row>
          <Callout className={styles['allocine-provider-form-banner']}>
            Pour le moment, seules les séances "classiques" peuvent être
            importées. Les séances spécifiques (3D, Dolby Atmos, 4DX...) ne
            génèreront pas d’offres. Nous travaillons actuellement à l’ajout de
            séances spécifiques.
          </Callout>
          <FormLayout.Actions
            className={styles['allocine-provider-form-actions']}
          >
            {!isCreatedEntity ? (
              <Button
                variant={ButtonVariant.SECONDARY}
                onClick={onCancel}
                type="button"
              >
                Annuler
              </Button>
            ) : (
              <></>
            )}

            <Button
              onClick={() => handleSubmit(formik.values)}
              type="button"
              isLoading={isLoading}
              disabled={
                !formik.isValid || typeof formik.values.price !== 'number'
              }
            >
              {isCreatedEntity ? 'Lancer la synchronisation' : 'Modifier'}
            </Button>
          </FormLayout.Actions>
        </>
      )}
    </FormikProvider>
  )
}
