import { useField, useFormikContext } from 'formik'
import { useEffect, useState } from 'react'

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

  const [showOtherAddress, setShowOtherAddress] = useState(false)
  const [manuallySetAddress, , { setValue: setManuallySetAddress }] =
    useField('manuallySetAddress')

  useEffect(() => {
    const offerlocation = formik.values.offerlocation

    if (!offerlocation) {
      return
    }

    // Display "other address" fields only if user checks "À une autre adresse"
    setShowOtherAddress(offerlocation === OFFER_LOCATION.OTHER_ADDRESS)
  }, [formik.values.offerlocation])

  // This will reset all address fields if user clicked on "Vous ne trouvez pas votre adresse ?"
  useEffect(() => {
    if (manuallySetAddress.value) {
      ;(async () => {
        await formik.setFieldValue('street', '')
        await formik.setFieldValue('postalCode', '')
        await formik.setFieldValue('city', '')
        await formik.setFieldValue('latitude', '')
        await formik.setFieldValue('longitude', '')
        await formik.setFieldValue('coords', '')
        await formik.setFieldValue('banId', '')
        await formik.setFieldValue('search-addressAutocomplete', '')
        await formik.setFieldValue('addressAutocomplete', '')
      })().catch(() => {})
    }
  }, [manuallySetAddress.value])

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
        />
      </FormLayout.Row>
      <FormLayout.Row className={styles['location-row']}>
        <RadioButton
          withBorder
          label="À une autre adresse"
          name="offerlocation"
          value={OFFER_LOCATION.OTHER_ADDRESS}
          required
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
              onClick={() => setManuallySetAddress(!manuallySetAddress.value)}
            >
              {!manuallySetAddress.value && (
                <>Vous ne trouvez pas votre adresse ?</>
              )}
              {manuallySetAddress.value && (
                <>Revenir à la sélection automatique</>
              )}
            </Button>
          </FormLayout.Row>
          {manuallySetAddress.value && <AddressManual />}
        </div>
      )}
    </FormLayout.Section>
  )
}
