import { useFormContext } from 'react-hook-form'
import { computeAddressDisplayName } from 'repository/venuesService'

import type { AdresseData } from '@/apiClient/adresse/types.ts'
import type { VenueListItemResponseModel } from '@/apiClient/v1'
import { FrontendError } from '@/commons/errors/FrontendError'
import { handleUnexpectedError } from '@/commons/errors/handleUnexpectedError'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullBackIcon from '@/icons/full-back.svg'
import fullNextIcon from '@/icons/full-next.svg'
import { OFFER_LOCATION } from '@/pages/IndividualOffer/commons/constants'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { AddressSelect } from '@/ui-kit/form/AddressSelect/AddressSelect'

import { EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES } from '../../../commons/constants'
import type { LocationFormValues } from '../../../commons/types'
import { AddressManualAdapter } from './AddressManualAdapter'
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
    resetField,
    watch,
    setValue,
    formState: { errors },
  } = useFormContext<LocationFormValues>()
  const isManualEdition = watch('address.isManualEdition')
  const isVenueAddress = watch('address.isVenueAddress')

  const readOnlyFieldsForAddressManual = isDisabled
    ? ['street', 'postalCode', 'city', 'coords']
    : []

  const toggleIsVenueAddress = () => {
    const willBeVenueAddress = !isVenueAddress

    if (willBeVenueAddress) {
      if (!venue.address) {
        return handleUnexpectedError(
          new FrontendError('`venue.address` is nullish.')
        )
      }

      setValue('address.inseeCode', venue.address.inseeCode ?? null)
      setValue('address.banId', venue.address.banId ?? null)
      setValue('address.city', venue.address.city)
      setValue('address.latitude', venue.address.latitude.toString())
      setValue('address.longitude', venue.address.longitude.toString())
      setValue(
        'address.coords',
        `${venue.address.latitude}, ${venue.address.longitude}`
      )
      setValue('address.postalCode', venue.address.postalCode)
      // TODO (igabriele, 2025-08-25): This should not be nullable. Investigate why we can receive a venue address without street since it's mandatory.
      // @ts-expect-error
      setValue('address.street', venue.address.street ?? null)
      setValue('address.label', venue.address.label ?? null)
      setValue('address.offerLocation', venue.address.id_oa.toString())
    } else {
      // @ts-expect-error We have to initialize with empty values to reset the address form.
      setValue('address', EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES)
    }

    setValue('address.isManualEdition', false)
    setValue('address.isVenueAddress', willBeVenueAddress)
  }

  const toggleIsManualEdition = () => {
    const willBeManualEdition = !isManualEdition

    if (willBeManualEdition) {
      resetField('address')
      setValue(
        'address',
        // @ts-expect-error We have to initialize with empty values to reset the address form.
        {
          ...EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES,
          isManualEdition: true,
        },
        { shouldDirty: false }
      )
    } else {
      setValue('address.isManualEdition', false)
    }
  }

  const updateAddressFromAutocomplete = (nextAddress: AdresseData) => {
    setValue('address.banId', nextAddress.id)
    setValue('address.city', nextAddress.city)
    setValue('address.inseeCode', nextAddress.inseeCode)
    setValue('address.isManualEdition', false)
    setValue('address.latitude', String(nextAddress.latitude))
    setValue('address.longitude', String(nextAddress.longitude))
    setValue('address.postalCode', nextAddress.postalCode)
    setValue('address.street', nextAddress.address, {
      shouldValidate: true,
    })
  }

  const venueFullText = `${venue.publicName || venue.name} – ${
    venue.address ? computeAddressDisplayName(venue.address, false) : null
  }`

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
        checkedOption={watch('address.offerLocation')}
        onChange={toggleIsVenueAddress}
        disabled={isDisabled}
        required
      />

      {!isVenueAddress && (
        <div className={styles['other-address-wrapper']}>
          <FormLayout.Row className={styles['location-row']}>
            <TextInput
              {...register('address.label')}
              label="Intitulé de la localisation"
              disabled={isDisabled}
            />
          </FormLayout.Row>
          <FormLayout.Row>
            {/*
              TODO (igabriele, 2025-08-25): Investigate ref issue in `AddressSelect`.

              We can't use `register` here because it produces a warning in console:
              `Warning: Function components cannot be given refs. Attempts to access this ref will fail. Did you mean to use React.forwardRef()?`
            */}
            <AddressSelect
              {...register('address.addressAutocomplete')}
              className={styles['location-field']}
              disabled={isManualEdition || isDisabled}
              error={errors.address?.addressAutocomplete?.message}
              label="Adresse postale"
              onAddressChosen={updateAddressFromAutocomplete}
            />
          </FormLayout.Row>

          <FormLayout.Row>
            <Button
              variant={ButtonVariant.QUATERNARY}
              icon={isManualEdition ? fullBackIcon : fullNextIcon}
              onClick={toggleIsManualEdition}
              disabled={isDisabled}
            >
              {isManualEdition
                ? `Revenir à la sélection automatique`
                : `Vous ne trouvez pas votre adresse ?`}
            </Button>
          </FormLayout.Row>

          {isManualEdition && (
            // Use adapter to map flat field expectations of AddressManual to nested address.* structure
            <AddressManualAdapter
              readOnlyFields={readOnlyFieldsForAddressManual}
            />
          )}
        </div>
      )}
    </>
  )
}
