import type React from 'react'
import { useState } from 'react'
import { useFormContext } from 'react-hook-form'
import { computeAddressDisplayName } from 'repository/venuesService'

import type { VenueListItemResponseModel } from '@/apiClient/v1'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import fullBackIcon from '@/icons/full-back.svg'
import fullNextIcon from '@/icons/full-next.svg'
import { OFFER_LOCATION } from '@/pages/IndividualOffer/commons/constants'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { AddressManual } from '@/ui-kit/form/AddressManual/AddressManual'
import { AddressSelect } from '@/ui-kit/form/AddressSelect/AddressSelect'
import { TextInput } from '@/ui-kit/form/TextInput/TextInput'

import type { LocationFormValues } from '../../../commons/types'
import styles from './PhysicalLocationSubform.module.scss'

export interface PhysicalLocationSubformProps {
  isDisabled: boolean
  venue: VenueListItemResponseModel
}

export const PhysicalLocationSubform = ({
  isDisabled,
  venue,
}: PhysicalLocationSubformProps): JSX.Element => {
  const {
    register,
    watch,
    setValue,
    formState: { errors },
  } = useFormContext<LocationFormValues>()
  const isManualEdition = watch('isManualEdition')
  const offerLocation = watch('offerLocation')

  const readOnlyFieldsForAddressManual = isDisabled
    ? ['street', 'postalCode', 'city', 'coords']
    : []

  const [showOtherAddress, setShowOtherAddress] = useState(
    offerLocation === OFFER_LOCATION.OTHER_ADDRESS
  )

  const onChangePhysicalLocationSubform = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const isVenueAddress = event.target.value !== OFFER_LOCATION.OTHER_ADDRESS
    setShowOtherAddress(!isVenueAddress)
    setValue('isManualEdition', false)

    if (isVenueAddress) {
      // If here, the user chose to use the venue address so
      // we reset the form fields with the related address values.

      // Avoid crashes if the venue doesn't have an OA, but this shouldn't technically happens
      if (!venue?.address) {
        return
      }

      setValue('inseeCode', venue.address.inseeCode ?? null)
      setValue('banId', venue.address.banId ?? null)
      setValue('city', venue.address.city)
      setValue('latitude', venue.address.latitude.toString())
      setValue('longitude', venue.address.longitude.toString())
      setValue(
        'coords',
        `${venue.address.latitude}, ${venue.address.longitude}`
      )
      setValue('postalCode', venue.address.postalCode)
      setValue('street', venue.address.street ?? null)
      setValue('locationLabel', venue.address.label ?? null)
      setValue('offerLocation', venue.address.id_oa.toString())
    } else {
      setValue('locationLabel', null)
      setValue('offerLocation', OFFER_LOCATION.OTHER_ADDRESS)
    }
  }

  const toggleManuallySetAddress = () => {
    setValue('isManualEdition', !isManualEdition)
  }

  const venueAddress = venue?.address
    ? computeAddressDisplayName(venue.address, false)
    : null
  const venueFullText = `${venue?.publicName || venue?.name} – ${venueAddress}`

  return (
    <>
      <RadioButtonGroup
        label="Il s’agit de l’adresse à laquelle les jeunes devront se présenter."
        name="offerLocation"
        variant="detailed"
        options={[
          {
            label: venueFullText,
            value: venue?.address?.id_oa.toString() ?? '',
          },
          {
            label: 'À une autre adresse',
            value: OFFER_LOCATION.OTHER_ADDRESS,
          },
        ]}
        checkedOption={offerLocation ?? undefined}
        onChange={onChangePhysicalLocationSubform}
        disabled={isDisabled}
      />
      {showOtherAddress && (
        <div className={styles['other-address-wrapper']}>
          <FormLayout.Row className={styles['location-row']}>
            <TextInput
              {...register('locationLabel')}
              label="Intitulé de la localisation"
              disabled={isDisabled}
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <AddressSelect
              {...register('addressAutocomplete')}
              label="Adresse postale"
              disabled={isManualEdition || isDisabled}
              className={styles['location-field']}
              error={errors.addressAutocomplete?.message}
              onAddressChosen={(addressData) => {
                setValue('isManualEdition', false)
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
              icon={isManualEdition ? fullBackIcon : fullNextIcon}
              onClick={toggleManuallySetAddress}
              disabled={isDisabled}
            >
              {isManualEdition
                ? `Revenir à la sélection automatique`
                : `Vous ne trouvez pas votre adresse ?`}
            </Button>
          </FormLayout.Row>

          {isManualEdition && (
            <AddressManual readOnlyFields={readOnlyFieldsForAddressManual} />
          )}
        </div>
      )}
    </>
  )
}
