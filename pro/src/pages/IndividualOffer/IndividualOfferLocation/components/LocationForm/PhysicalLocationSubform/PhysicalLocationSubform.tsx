import { useFormContext } from 'react-hook-form'
import { computeAddressDisplayName } from 'repository/venuesService'

import type { AdresseData } from '@/apiClient/adresse/types.ts'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { AddressFields } from '@/components/AddressFields/AddressFields'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { OFFER_LOCATION } from '@/pages/IndividualOffer/commons/constants'
import { AddressManual } from '@/ui-kit/form/AddressManual/AddressManual'

import { EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES } from '../../../commons/constants'
import type { LocationFormValues } from '../../../commons/types'
import styles from './PhysicalLocationSubform.module.scss'

export interface PhysicalLocationSubformProps {
  isDisabled: boolean
}

export const PhysicalLocationSubform = ({
  isDisabled,
}: PhysicalLocationSubformProps): JSX.Element => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const {
    register,
    resetField,
    watch,
    setValue,
    formState: { errors },
  } = useFormContext<LocationFormValues>()
  const isManualEdition = watch('location.isManualEdition')
  const isVenueAddress = watch('location.isVenueLocation')

  const readOnlyFieldsForAddressManual = isDisabled
    ? ['street', 'postalCode', 'city', 'coords']
    : []

  const toggleIsVenueAddress = () => {
    const willBeVenueAddress = !isVenueAddress

    if (willBeVenueAddress) {
      setValue(
        'location.inseeCode',
        selectedPartnerVenue.location.inseeCode ?? null
      )
      setValue('location.banId', selectedPartnerVenue.location.banId ?? null)
      setValue('location.city', selectedPartnerVenue.location.city)
      setValue(
        'location.latitude',
        selectedPartnerVenue.location.latitude.toString()
      )
      setValue(
        'location.longitude',
        selectedPartnerVenue.location.longitude.toString()
      )
      setValue(
        'location.coords',
        `${selectedPartnerVenue.location.latitude}, ${selectedPartnerVenue.location.longitude}`
      )
      setValue('location.postalCode', selectedPartnerVenue.location.postalCode)
      // TODO (igabriele, 2025-08-25): This should not be nullable. Investigate why we can receive a venue location without street since it's mandatory.
      setValue('location.street', selectedPartnerVenue.location.street ?? null)
      setValue('location.label', selectedPartnerVenue.location.label ?? null)
      setValue(
        'location.offerLocation',
        selectedPartnerVenue.location.id.toString()
      )
    } else {
      setValue('location', EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES)
    }

    setValue('location.isManualEdition', false)
    setValue('location.isVenueLocation', willBeVenueAddress)
  }

  const toggleIsManualEdition = () => {
    const willBeManualEdition = !isManualEdition

    if (willBeManualEdition) {
      resetField('location', {
        defaultValue: {
          ...EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES,
          isManualEdition: true,
          label: watch('location.label'),
        },
      })
    } else {
      setValue('location.isManualEdition', false)
    }
  }

  const updateAddressFromAutocomplete = (nextAddress: AdresseData) => {
    setValue('location.banId', nextAddress.id)
    setValue('location.city', nextAddress.city)
    setValue('location.inseeCode', nextAddress.inseeCode)
    setValue('location.isManualEdition', false)
    setValue('location.latitude', String(nextAddress.latitude))
    setValue('location.longitude', String(nextAddress.longitude))
    setValue('location.postalCode', nextAddress.postalCode)
    setValue('location.street', nextAddress.address, {
      shouldValidate: true,
    })
  }

  const venueFullText = `${selectedPartnerVenue.publicName} – ${computeAddressDisplayName(
    selectedPartnerVenue.location,
    false
  )}`

  return (
    <>
      <FormLayout.Row mdSpaceAfter>
        <RadioButtonGroup
          label="Il s’agit de l’adresse à laquelle les jeunes devront se présenter."
          name="offerLocation"
          variant="detailed"
          options={[
            {
              label: venueFullText,
              value: selectedPartnerVenue.location.id.toString(),
            },
            {
              label: 'À une autre adresse',
              value: OFFER_LOCATION.OTHER_ADDRESS,
            },
          ]}
          checkedOption={watch('location.offerLocation')}
          onChange={toggleIsVenueAddress}
          disabled={isDisabled}
        />
      </FormLayout.Row>
      {!isVenueAddress && (
        <>
          <FormLayout.Row mdSpaceAfter>
            <TextInput
              {...register('location.label')}
              label="Intitulé de la localisation"
              disabled={isDisabled}
            />
          </FormLayout.Row>

          <AddressFields
            addressRegister={register('location.addressAutocomplete')}
            className={styles['location-field']}
            disabled={isDisabled}
            error={errors.location?.addressAutocomplete?.message}
            onAddressChosen={updateAddressFromAutocomplete}
            renderManual={() => (
              <AddressManual
                readOnlyFields={readOnlyFieldsForAddressManual}
                prefix="location."
              />
            )}
            manual={isManualEdition}
            onManualChange={toggleIsManualEdition}
          />
        </>
      )}
    </>
  )
}
