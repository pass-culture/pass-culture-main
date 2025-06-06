import React, { useEffect, useState } from 'react'
import { useFormContext } from 'react-hook-form'

import { VenueListItemResponseModel } from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullBackIcon from 'icons/full-back.svg'
import fullNextIcon from 'icons/full-next.svg'
import { OFFER_LOCATION } from 'pages/IndividualOffer/commons/constants'
import { IndividualOfferFormValues } from 'pages/IndividualOffer/commons/types'
import { computeAddressDisplayName } from 'repository/venuesService'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { AddressManual } from 'ui-kit/formV2/AddressManual/AddressManual'
import { AddressSelect } from 'ui-kit/formV2/AddressSelect/AddressSelect'
import { RadioGroup } from 'ui-kit/formV2/RadioGroup/RadioGroup'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import styles from './OfferLocation.module.scss'

interface OfferLocationProps {
  venue: VenueListItemResponseModel | undefined
  readOnlyFields: string[]
}

export const OfferLocation = ({
  venue,
  readOnlyFields,
}: OfferLocationProps): JSX.Element => {
  const methods = useFormContext<IndividualOfferFormValues>() // retrieve all hook methods

  const {
    register,
    getValues,
    setValue,
    watch,
    formState: { errors },
  } = methods

  const [showOtherAddress, setShowOtherAddress] = useState(
    getValues('offerLocation') === OFFER_LOCATION.OTHER_ADDRESS
  )

  useEffect(() => {
    setShowOtherAddress(getValues('offerLocation') === 'other')
  }, [getValues])

  const onChangeOfferLocation = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setValue('offerLocation', event.target.value)
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
        setValue('manuallySetAddress', false),
        setValue('inseeCode', venue.address.inseeCode),
        setValue('banId', venue.address.banId),
        setValue('city', venue.address.city),
        setValue('locationLabel', venue.address.label),
        setValue('latitude', venue.address.latitude.toString()),
        setValue('longitude', venue.address.longitude.toString()),
        setValue(
          'coords',
          `${venue.address.latitude}, ${venue.address.longitude}`
        ),
        setValue('postalCode', venue.address.postalCode),
        setValue('street', venue.address.street),
      ])
    } else {
      //   await resetAddressFieldsHook({ methods })
      setValue('locationLabel', '')
    }
  }

  const toggleManuallySetAddress = async () => {
    //   await resetAddressFieldsHook({ methods })

    const isAddressManual = !getValues('manuallySetAddress')
    setValue('manuallySetAddress', isAddressManual)
  }

  const venueAddress = venue?.address
    ? computeAddressDisplayName(venue.address, false)
    : ''

  return (
    <FormLayout.Section
      title="Localisation de l’offre"
      className={styles['offer-location-wrapper']}
    >
      <FormLayout.Row className={styles['location-row']}>
        <RadioGroup
          name="offerLocation"
          checkedOption={watch('offerLocation')}
          onChange={onChangeOfferLocation}
          group={[
            {
              label: `${venue?.publicName || venue?.name} – ${venueAddress}`,
              value: venue?.address?.id_oa.toString() ?? '',
            },
            {
              label: 'À une autre adresse',
              value: OFFER_LOCATION.OTHER_ADDRESS,
            },
          ]}
          disabled={readOnlyFields.includes('offerLocation')}
          legend="Il s’agit de l’adresse à laquelle les jeunes devront se présenter."
          variant={RadioVariant.BOX}
        />
      </FormLayout.Row>
      {showOtherAddress && (
        <div className={styles['other-address-wrapper']}>
          <FormLayout.Row className={styles['location-row']}>
            <TextInput
              {...register('locationLabel')}
              label="Intitulé de la localisation"
              name="locationLabel"
              disabled={readOnlyFields.includes('locationLabel')}
            />
          </FormLayout.Row>

          <FormLayout.Row>
            <AddressSelect
              {...register('addressAutocomplete')}
              disabled={
                getValues('manuallySetAddress') ||
                readOnlyFields.includes('addressAutocomplete')
              }
              className={styles['location-field']}
              label={'Adresse postale'}
              error={errors.addressAutocomplete?.message}
              onAddressChosen={(addressData) => {
                setValue('street', addressData.address)
                setValue('postalCode', addressData.postalCode)
                setValue('city', addressData.city)
                setValue('latitude', String(addressData.latitude))
                setValue('longitude', String(addressData.longitude))
                setValue('banId', addressData.id)
                setValue('inseeCode', addressData.inseeCode)
              }}
            />
          </FormLayout.Row>

          <FormLayout.Row>
            <Button
              variant={ButtonVariant.QUATERNARY}
              icon={
                getValues('manuallySetAddress') ? fullBackIcon : fullNextIcon
              }
              onClick={toggleManuallySetAddress}
              disabled={readOnlyFields.includes('manuallySetAddress')}
            >
              {getValues('manuallySetAddress') ? (
                <>Revenir à la sélection automatique</>
              ) : (
                <>Vous ne trouvez pas votre adresse ?</>
              )}
            </Button>
          </FormLayout.Row>
          {getValues('manuallySetAddress') && (
            <AddressManual readOnlyFields={readOnlyFields} />
          )}
        </div>
      )}
    </FormLayout.Section>
  )
}
