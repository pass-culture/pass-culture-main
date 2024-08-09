import { useField, useFormikContext } from 'formik'
import React, { useState } from 'react'

import { VenueListItemResponseModel } from 'apiClient/v1'
import { AddressSelect } from 'components/Address/Address'
import { AddressManual } from 'components/AddressManual/AddressManual'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullBackIcon from 'icons/full-back.svg'
import fullNextIcon from 'icons/full-next.svg'
import { computeAddressDisplayName } from 'repository/venuesService'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { RadioButton } from 'ui-kit/form/RadioButton/RadioButton'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import { IndividualOfferFormValues } from '../types'
import { resetAddressFields } from '../utils/resetAddressFields'

import { OFFER_LOCATION } from './constants'
import styles from './OfferLocation.module.scss'

interface OfferLocationProps {
  venue: VenueListItemResponseModel | undefined
}

export const OfferLocation = ({ venue }: OfferLocationProps): JSX.Element => {
  const formik = useFormikContext<IndividualOfferFormValues>()

  const [showOtherAddress, setShowOtherAddress] = useState(
    formik.values.offerlocation === OFFER_LOCATION.OTHER_ADDRESS
  )
  const [manuallySetAddress, , { setValue: setManuallySetAddress }] =
    useField('manuallySetAddress')

  const onChangeOfferLocation = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const isVenueAddress = event.target.value !== OFFER_LOCATION.OTHER_ADDRESS
    setShowOtherAddress(!isVenueAddress)
    if (isVenueAddress) {
      // If here, the user chose to use the venue address
      // Manually set the form fields with venue address values

      // Avoid crashes if the venue doesn't have an OA, but this shouldn't technically happens
      if (!venue?.address) {
        return
      }

      await Promise.all([
        formik.setFieldValue('banId', venue.address.banId),
        formik.setFieldValue('city', venue.address.city),
        formik.setFieldValue('locationLabel', venue.address.label),
        formik.setFieldValue('latitude', venue.address.latitude),
        formik.setFieldValue('longitude', venue.address.longitude),
        formik.setFieldValue(
          'coords',
          `${venue.address.latitude}, ${venue.address.longitude}`
        ),
        formik.setFieldValue('postalCode', venue.address.postalCode),
        formik.setFieldValue('street', venue.address.street),
      ])
    } else {
      await resetAddressFields({ formik })
    }
  }

  const toggleManuallySetAddress = async () => {
    const isAddressManual = !manuallySetAddress.value
    await setManuallySetAddress(isAddressManual)
    if (isAddressManual) {
      await resetAddressFields({ formik })
    }
  }

  const venueAddress = venue?.address
    ? computeAddressDisplayName(venue.address, false)
    : ''
  const venueFullText = `${venue?.publicName ?? venue?.name} – ${venueAddress}`

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
          label={venueFullText}
          name="offerlocation"
          value={venueFullText}
          required
          onChange={onChangeOfferLocation}
        />
      </FormLayout.Row>
      <FormLayout.Row className={styles['location-row']}>
        <RadioButton
          withBorder
          label="À une autre adresse"
          name="offerlocation"
          value={OFFER_LOCATION.OTHER_ADDRESS}
          required
          onChange={onChangeOfferLocation}
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
              onClick={toggleManuallySetAddress}
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
