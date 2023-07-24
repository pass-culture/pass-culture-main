import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'

import { PostVenueProviderBody } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { SynchronizationEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { validationSchema } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/VenueProvidersManager/AllocineProviderForm/validationSchema'
import { Banner, Button, Checkbox, InfoBox, TextInput } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import './AllocineProviderForm.scss'

interface FormValuesProps {
  isDuo: boolean
  price: number | string
  quantity: number | string
  isActive?: boolean
}

export interface AllocineProviderFormProps {
  saveVenueProvider: (payload: PostVenueProviderBody) => void
  providerId: number
  offererId: number
  venueId: number
  isCreatedEntity?: boolean
  onCancel?: () => void
  initialValues?: FormValuesProps
}

const AllocineProviderForm = ({
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

  const handleSubmit = (formValues: FormValuesProps) => {
    const { isDuo = true, price } = formValues
    const quantity =
      formValues.quantity !== '' && formValues.quantity !== undefined
        ? Number(formValues.quantity)
        : undefined

    const payload = {
      quantity,
      isDuo,
      price: String(price),
      providerId,
      venueId,
      isActive: initialValues?.isActive,
    }

    setIsLoading(true)

    saveVenueProvider(payload)
    logEvent?.(SynchronizationEvents.CLICKED_IMPORT, {
      offererId: offererId,
      venueId: venueId,
      providerId: providerId,
    })
  }

  const formik = useFormik({
    initialValues,
    onSubmit: handleSubmit,
    validationSchema,
  })

  return (
    <FormikProvider value={formik}>
      <FormLayout>
        {!isLoading && (
          <>
            <FormLayout.Row
              sideComponent={
                isCreatedEntity ? (
                  <InfoBox>Prix auquel la place de cinéma sera vendue.</InfoBox>
                ) : (
                  <></>
                )
              }
            >
              <TextInput
                name="price"
                type="number"
                label="Prix de vente/place"
                min="0"
                placeholder="Ex : 12€"
                step={0.01}
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
              />
            </FormLayout.Row>
            <FormLayout.Row
              sideComponent={
                isCreatedEntity ? (
                  <InfoBox>
                    En activant cette option, vous permettez au bénéficiaire du
                    pass Culture de venir accompagné. La seconde place sera
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
            <FormLayout.Row>
              <Banner type="notification-info">
                <p>
                  Pour le moment, seules les séances "classiques" peuvent être
                  importées.
                </p>
                <p>
                  Les séances spécifiques (3D, Dolby Atmos, 4DX...) ne
                  génèreront pas d’offres.
                </p>
                <p>
                  Nous travaillons actuellement à l’ajout de séances
                  spécifiques.
                </p>
              </Banner>
            </FormLayout.Row>
            <FormLayout.Actions>
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
                {isCreatedEntity ? 'Importer les offres' : 'Modifier'}
              </Button>
            </FormLayout.Actions>
          </>
        )}
      </FormLayout>
    </FormikProvider>
  )
}

export default AllocineProviderForm
