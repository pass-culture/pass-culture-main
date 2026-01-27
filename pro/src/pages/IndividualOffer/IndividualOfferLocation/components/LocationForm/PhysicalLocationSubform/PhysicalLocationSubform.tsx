import { useFormContext } from 'react-hook-form'
import { computeAddressDisplayName } from 'repository/venuesService'

import type { AdresseData } from '@/apiClient/adresse/types.ts'
import type { VenueListItemResponseModel } from '@/apiClient/v1'
import { FrontendError } from '@/commons/errors/FrontendError'
import { handleUnexpectedError } from '@/commons/errors/handleUnexpectedError'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullBackIcon from '@/icons/full-back.svg'
import fullNextIcon from '@/icons/full-next.svg'
import { OFFER_LOCATION } from '@/pages/IndividualOffer/commons/constants'
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
  const isManualEdition = watch('location.isManualEdition')
  const isVenueAddress = watch('location.isVenueLocation')

  const readOnlyFieldsForAddressManual = isDisabled
    ? ['street', 'postalCode', 'city', 'coords']
    : []

  const toggleIsVenueAddress = () => {
    const willBeVenueAddress = !isVenueAddress

    if (willBeVenueAddress) {
      if (!venue.location) {
        return handleUnexpectedError(
          new FrontendError('`venue.location` is nullish.')
        )
      }

      setValue('location.inseeCode', venue.location.inseeCode ?? null)
      setValue('location.banId', venue.location.banId ?? null)
      setValue('location.city', venue.location.city)
      setValue('location.latitude', venue.location.latitude.toString())
      setValue('location.longitude', venue.location.longitude.toString())
      setValue(
        'location.coords',
        `${venue.location.latitude}, ${venue.location.longitude}`
      )
      setValue('location.postalCode', venue.location.postalCode)
      // TODO (igabriele, 2025-08-25): This should not be nullable. Investigate why we can receive a venue location without street since it's mandatory.
      setValue('location.street', venue.location.street ?? null)
      setValue('location.label', venue.location.label ?? null)
      setValue('location.offerLocation', venue.location.id.toString())
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

  const venueFullText = `${venue.publicName} – ${
    venue.location ? computeAddressDisplayName(venue.location, false) : null
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
            value: venue?.location?.id.toString() ?? '',
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

      {!isVenueAddress && (
        <div className={styles['other-address-wrapper']}>
          <FormLayout.Row className={styles['location-row']}>
            <TextInput
              {...register('location.label')}
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
              {...register('location.addressAutocomplete')}
              className={styles['location-field']}
              disabled={isManualEdition || isDisabled}
              error={errors.location?.addressAutocomplete?.message}
              label="Adresse postale"
              onAddressChosen={updateAddressFromAutocomplete}
            />
          </FormLayout.Row>

          <FormLayout.Row className={styles['manual-address-button']}>
            <Button
              type="button"
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              icon={isManualEdition ? fullBackIcon : fullNextIcon}
              onClick={toggleIsManualEdition}
              disabled={isDisabled}
              label={
                isManualEdition
                  ? `Revenir à la sélection automatique`
                  : `Vous ne trouvez pas votre adresse ?`
              }
            />
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
