import { useState } from 'react'
import { useFormContext } from 'react-hook-form'

import { AdresseData } from 'apiClient/adresse/types'
import {
  CollectiveLocationType,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { resetReactHookFormAddressFields } from 'commons/utils/resetAddressFields'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullBackIcon from 'icons/full-back.svg'
import fullNextIcon from 'icons/full-next.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { AddressManual } from 'ui-kit/form/AddressManual/AddressManual'
import { AddressSelect } from 'ui-kit/form/AddressSelect/AddressSelect'
import { RadioGroup, RadioGroupProps } from 'ui-kit/form/RadioGroup/RadioGroup'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from '../OfferEducationalForm.module.scss'

import { InterventionAreaMultiSelect } from './InterventionAreaMultiSelect'
export interface FormLocationProps {
  disableForm: boolean
  venues: VenueListItemResponseModel[]
}

export const FormLocation = ({
  venues,
  disableForm,
}: FormLocationProps): JSX.Element => {
  const { watch, setValue, register, getFieldState } =
    useFormContext<OfferEducationalFormValues>()
  const [shouldShowManualAddressForm, setShouldShowManualAddressForm] =
    useState(watch('location.address')?.isManualEdition)

  const selectedVenue = venues.find((v) => v.id.toString() === watch('venueId'))

  const toggleManualAddressForm = () => {
    setShouldShowManualAddressForm(!shouldShowManualAddressForm)
    if (!shouldShowManualAddressForm) {
      setValue('location.address.isVenueAddress', false)
      setValue('location.address.isManualEdition', true)
      resetReactHookFormAddressFields((name, defaultValue) =>
        setValue(name, defaultValue)
      )
    }
  }

  const setVenueAddressFields = () => {
    const { address } = selectedVenue || {}
    setValue('banId', address?.banId)
    setValue('city', address?.city)
    setValue('longitude', (address?.longitude || '').toString())
    setValue('latitude', (address?.latitude || '').toString())
    setValue('postalCode', address?.postalCode)
    setValue('street', address?.street)
    setValue('inseeCode', address?.inseeCode)
    setValue('location.address.label', address?.label || undefined)
    setValue('location.address.isVenueAddress', true)
    setValue('location.address.isManualEdition', false)
    setValue('coords', `${address?.latitude}, ${address?.longitude}`)
  }

  const handleAddressLocationChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setValue('location.address.id_oa', event.target.value)

    const isSpecificAddress = event.target.value === 'SPECIFIC_ADDRESS'

    if (isSpecificAddress) {
      setValue('location.address.label', '')
      resetReactHookFormAddressFields((name, defaultValue) => {
        setValue(name, defaultValue)
      })
    } else {
      // If here, the user chose to use the venue address
      setVenueAddressFields()
    }
  }

  const onAddressSelect = (data: AdresseData) => {
    setValue('location.address.isVenueAddress', false)
    setValue('location.address.isManualEdition', false)
    setValue('street', data.address)
    setValue('postalCode', data.postalCode)
    setValue('city', data.city)
    setValue('latitude', data.latitude.toString())
    setValue('longitude', data.longitude.toString())
    setValue('banId', data.id)
    setValue('inseeCode', data.inseeCode)
    setValue('coords', `${data.latitude}, ${data.longitude}`)
  }

  const locationTypeRadios: RadioGroupProps['group'] = [
    {
      label: 'À une adresse précise',
      value: CollectiveLocationType.ADDRESS,
      sizing: 'fill',
      collapsed: (
        <RadioGroup
          onChange={handleAddressLocationChange}
          disabled={disableForm}
          legend="Type d'adresse *"
          variant="detailed"
          checkedOption={watch('location.address.id_oa')}
          name="location.address.id_oa"
          group={[
            {
              label: selectedVenue
                ? `${selectedVenue.address?.label} - ${selectedVenue.address?.street}
                  ${selectedVenue.address?.postalCode} ${selectedVenue.address?.city}`
                : 'Adresse du lieu sélectionné',
              value: selectedVenue?.address?.id_oa.toString() ?? '',
              sizing: 'fill',
            },
            {
              label: 'Autre adresse',
              value: 'SPECIFIC_ADDRESS',
              sizing: 'fill',
              collapsed: (
                <div className={styles['specific-address']}>
                  <TextInput
                    label="Intitulé de la localisation"
                    {...register('location.address.label')}
                    error={
                      getFieldState('location.address.label').error?.message
                    }
                    disabled={disableForm}
                  />
                  <AddressSelect
                    disabled={disableForm || shouldShowManualAddressForm}
                    onAddressChosen={onAddressSelect}
                    label="Adresse postale"
                    {...register('addressAutocomplete')}
                    className={styles['specific-address-search']}
                    error={getFieldState('addressAutocomplete').error?.message}
                  />
                  <Button
                    variant={ButtonVariant.QUATERNARY}
                    icon={
                      shouldShowManualAddressForm ? fullBackIcon : fullNextIcon
                    }
                    onClick={toggleManualAddressForm}
                    disabled={disableForm}
                  >
                    {shouldShowManualAddressForm ? (
                      <>Revenir à la sélection automatique</>
                    ) : (
                      <>Vous ne trouvez pas votre adresse ?</>
                    )}
                  </Button>
                  {shouldShowManualAddressForm && (
                    <AddressManual
                      gpsCalloutMessage={
                        'Les coordonnées GPS sont des informations à ne pas négliger. Elles permettent aux enseignants de trouver votre offre sur ADAGE.'
                      }
                      readOnlyFields={
                        disableForm
                          ? ['city', 'street', 'postalCode', 'coords']
                          : []
                      }
                    />
                  )}
                </div>
              ),
            },
          ]}
        />
      ),
    },
    {
      label: 'En établissement scolaire',
      value: CollectiveLocationType.SCHOOL,
      sizing: 'fill',
      collapsed: (
        <InterventionAreaMultiSelect
          label="Indiquez aux enseignants les départements dans lesquels vous
            proposez votre offre."
          disabled={disableForm}
        />
      ),
    },
    {
      label: 'À déterminer avec l’enseignant',
      value: CollectiveLocationType.TO_BE_DEFINED,
      sizing: 'fill',
      collapsed: (
        <>
          <InterventionAreaMultiSelect
            label="Même si le lieu reste à définir, précisez aux enseignants les départements dans lesquels vous proposez votre offre."
            disabled={disableForm}
          />
          <TextArea
            label="Commentaire"
            maxLength={200}
            {...register('location.locationComment')}
            error={getFieldState('location.locationComment').error?.message}
          />
        </>
      ),
    },
  ]

  const handleLocationTypeChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setValue(
      'location.locationType',
      event.target.value as CollectiveLocationType
    )
    if (event.target.value === CollectiveLocationType.ADDRESS) {
      const { address } = selectedVenue || {}
      // If here, the user chose to use the venue address
      setVenueAddressFields()
      setValue('location.address.id_oa', address?.id_oa.toString())
      setValue('location.locationType', CollectiveLocationType.ADDRESS)
      setValue('location.locationComment', '')
      setValue('interventionArea', [])
    } else {
      resetReactHookFormAddressFields((name, defaultValue) =>
        setValue(name, defaultValue)
      )
    }
  }

  return (
    <FormLayout.Row>
      <RadioGroup
        onChange={handleLocationTypeChange}
        group={locationTypeRadios}
        variant="detailed"
        legend={
          <h2 className={styles['subtitle']}>Où se déroule votre offre ? *</h2>
        }
        name="location.locationType"
        disabled={disableForm}
        checkedOption={watch('location.locationType')}
      />
    </FormLayout.Row>
  )
}
