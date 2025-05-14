import { useField, useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import { VenueListItemResponseModel } from 'apiClient/v1'
import { resetAddressFields } from 'commons/utils/resetAddressFields'
import { AddressSelect } from 'components/Address/Address'
import { AddressManual } from 'components/AddressManual/AddressManual'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullBackIcon from 'icons/full-back.svg'
import fullNextIcon from 'icons/full-next.svg'
import { OFFER_LOCATION } from 'pages/IndividualOffer/commons/constants'
import { IndividualOfferFormValues } from 'pages/IndividualOffer/commons/types'
import { computeAddressDisplayName } from 'repository/venuesService'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { RadioButton } from 'ui-kit/form/RadioButton/RadioButton'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './OfferLocation.module.scss'

interface OfferLocationProps {
  venue: VenueListItemResponseModel | undefined
  readOnlyFields: string[]
}

export const OfferLocation = ({
  venue,
  readOnlyFields,
}: OfferLocationProps): JSX.Element => {
  const formik = useFormikContext<IndividualOfferFormValues>()

  const [showOtherAddress, setShowOtherAddress] = useState(
    formik.values.offerLocation === OFFER_LOCATION.OTHER_ADDRESS
  )

  useEffect(() => {
    setShowOtherAddress(formik.values.offerLocation === 'other')
  }, [formik.values.offerLocation])

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
        formik.setFieldValue('manuallySetAddress', false),
        formik.setFieldValue('inseeCode', venue.address.inseeCode),
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
      await formik.setFieldValue('locationLabel', '')
      await formik.setFieldTouched('locationLabel', false)
    }
  }

  const toggleManuallySetAddress = async () => {
    const isAddressManual = !manuallySetAddress.value
    await setManuallySetAddress(isAddressManual)
    await resetAddressFields({ formik })
  }

  const venueAddress = venue?.address
    ? computeAddressDisplayName(venue.address, false)
    : ''
  const venueFullText = `${venue?.publicName || venue?.name} – ${venueAddress}`
  return (
    <FormLayout.Section
      title="Localisation de l’offre"
      className={styles['offer-location-wrapper']}
    >
      <p className={styles['infotext']}>
        Il s’agit de l’adresse à laquelle les jeunes devront se présenter.
      </p>
      <FormLayout.Row className={styles['location-row']}>
        <RadioButton
          variant={RadioVariant.BOX}
          label={venueFullText}
          name="offerLocation"
          value={venue?.address?.id_oa.toString() ?? ''}
          required
          onChange={onChangeOfferLocation}
          disabled={readOnlyFields.includes('offerLocation')}
        />
      </FormLayout.Row>
      <FormLayout.Row className={styles['location-row']}>
        <RadioButton
          variant={RadioVariant.BOX}
          label="À une autre adresse"
          name="offerLocation"
          value={OFFER_LOCATION.OTHER_ADDRESS}
          required
          onChange={onChangeOfferLocation}
          disabled={readOnlyFields.includes('offerLocation')}
        />
      </FormLayout.Row>
      {showOtherAddress && (
        <div className={styles['other-address-wrapper']}>
          <FormLayout.Row className={styles['location-row']}>
            <TextInput
              label="Intitulé de la localisation"
              name="locationLabel"
              isOptional
              disabled={readOnlyFields.includes('locationLabel')}
            />
          </FormLayout.Row>

          <FormLayout.Row>
            <AddressSelect
              disabled={
                manuallySetAddress.value ||
                readOnlyFields.includes('addressAutocomplete')
              }
              className={styles['location-field']}
            />
          </FormLayout.Row>

          <FormLayout.Row>
            <Button
              variant={ButtonVariant.QUATERNARY}
              icon={manuallySetAddress.value ? fullBackIcon : fullNextIcon}
              onClick={toggleManuallySetAddress}
              disabled={readOnlyFields.includes('manuallySetAddress')}
            >
              {manuallySetAddress.value ? (
                <>Revenir à la sélection automatique</>
              ) : (
                <>Vous ne trouvez pas votre adresse ?</>
              )}
            </Button>
          </FormLayout.Row>
          {manuallySetAddress.value && (
            <AddressManual readOnlyFields={readOnlyFields} />
          )}
        </div>
      )}
    </FormLayout.Section>
  )
}
