import { useField, useFormikContext } from 'formik'
import React, { useState } from 'react'

import { VenueListItemResponseModel } from 'apiClient/v1'
import { AddressSelect } from 'components/Address/Address'
import { AddressManual } from 'components/AddressManual/AddressManual'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullBackIcon from 'icons/full-back.svg'
import fullNextIcon from 'icons/full-next.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { RadioButton } from 'ui-kit/form/RadioButton/RadioButton'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import { IndividualOfferFormValues } from '../types'

import { OFFER_LOCATION } from './constants'
import styles from './OfferLocation.module.scss'

export interface OfferLocationProps {
  venue: VenueListItemResponseModel | undefined
}

export const OfferLocation = ({ venue }: OfferLocationProps): JSX.Element => {
  const formik = useFormikContext<IndividualOfferFormValues>()

  const [showOtherAddress, setShowOtherAddress] = useState(
    formik.values.offerlocation === OFFER_LOCATION.OTHER_ADDRESS
  )
  const [manuallySetAddress, , { setValue: setManuallySetAddress }] =
    useField('manuallySetAddress')

  const onManuallySetAddress = async () => {
    const newValue = !manuallySetAddress.value
    await setManuallySetAddress(newValue)
    if (newValue) {
      const fieldsToUpdate = [
        'street',
        'postalCode',
        'city',
        'latitude',
        'longitude',
        'coords',
        'banId',
        'search-addressAutocomplete',
        'addressAutocomplete',
      ]

      // Empty all fields value
      await Promise.all(
        fieldsToUpdate.map((fieldName) => formik.setFieldValue(fieldName, ''))
      )

      // Make all fields untouched
      // (This will prevent validation errors to be shown if user previously touched those fields, then switched that trigger OFF, then ON again)
      await Promise.all(
        fieldsToUpdate.map((fieldName) =>
          formik.setFieldTouched(fieldName, false)
        )
      )
    }
  }

  const venueLabel = `${
    venue?.publicName ? `${venue.publicName} – ` : ''
  }« Adresse de l'OA »`

  return (
    <FormLayout.Section
      title="Localisation de l'offre"
      className={styles['offerlocation-wrapper']}
    >
      <p className={styles['infotext']}>
        Il s’agit de l’adresse à laquelle votre public devra se présenter.
      </p>
      <FormLayout.Row className={styles['location-row']}>
        <RadioButton
          withBorder
          label={venueLabel}
          name="offerlocation"
          value={"« Adresse de l'OA »"}
          required
          onChange={() => setShowOtherAddress(false)}
        />
      </FormLayout.Row>
      <FormLayout.Row className={styles['location-row']}>
        <RadioButton
          withBorder
          label="À une autre adresse"
          name="offerlocation"
          value={OFFER_LOCATION.OTHER_ADDRESS}
          required
          onChange={() => setShowOtherAddress(true)}
        />
      </FormLayout.Row>
      {showOtherAddress && (
        <div className={styles['other-address-wrapper']}>
          <FormLayout.Row className={styles['location-row']}>
            <TextInput
              label="Intitulé de la localisation"
              name="locationLabel"
              isOptional
            />
          </FormLayout.Row>

          <FormLayout.Row>
            <AddressSelect
              disabled={manuallySetAddress.value}
              className={styles['location-field']}
            />
          </FormLayout.Row>

          <FormLayout.Row>
            <Button
              variant={ButtonVariant.QUATERNARY}
              title="Renseignez l’adresse manuellement"
              icon={manuallySetAddress.value ? fullBackIcon : fullNextIcon}
              onClick={onManuallySetAddress}
            >
              {manuallySetAddress.value ? (
                <>Revenir à la sélection automatique</>
              ) : (
                <>Vous ne trouvez pas votre adresse ?</>
              )}
            </Button>
          </FormLayout.Row>
          {manuallySetAddress.value && <AddressManual />}
        </div>
      )}
    </FormLayout.Section>
  )
}
