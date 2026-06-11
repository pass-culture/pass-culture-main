import { useRef } from 'react'
import { useFormContext } from 'react-hook-form'

import type { AdresseData } from '@/apiClient/adresse/types'
import { CollectiveLocationType } from '@/apiClient/v1/new'
import type { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { resetReactHookFormAddressFields } from '@/commons/utils/resetAddressFields'
import { AddressFields } from '@/components/AddressFields/AddressFields'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { AddressManual } from '@/ui-kit/form/AddressManual/AddressManual'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import styles from '../OfferEducationalForm.module.scss'
import { InterventionAreaMultiSelect } from './InterventionAreaMultiSelect'
export interface FormLocationProps {
  disableForm: boolean
}

export const FormLocation = ({
  disableForm,
}: FormLocationProps): JSX.Element => {
  const { watch, setValue, register, getFieldState } =
    useFormContext<OfferEducationalFormValues>()
  const isManualEdition = watch('location.location.isManualEdition')

  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const toggleManualAddressForm = () => {
    setValue('location.location.isManualEdition', !isManualEdition)
    if (!isManualEdition) {
      setValue('location.location.isVenueLocation', false)
      setValue('location.location.isManualEdition', true)
      resetReactHookFormAddressFields<OfferEducationalFormValues>(
        (name, defaultValue) => setValue(name, defaultValue)
      )
    }
  }

  const setVenueAddressFields = () => {
    const { location } = selectedPartnerVenue || {}
    setValue('banId', location?.banId)
    setValue('city', location?.city)
    setValue('longitude', (location?.longitude || '').toString())
    setValue('latitude', (location?.latitude || '').toString())
    setValue('postalCode', location?.postalCode)
    setValue('street', location?.street)
    setValue('inseeCode', location?.inseeCode)
    setValue('location.location.label', location?.label || undefined)
    setValue('location.location.isVenueLocation', true)
    setValue('location.location.isManualEdition', false)
    setValue('coords', `${location?.latitude}, ${location?.longitude}`)
  }

  const handleAddressLocationChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setValue('location.location.id', event.target.value)

    const isSpecificAddress = event.target.value === 'SPECIFIC_ADDRESS'

    if (isSpecificAddress) {
      setValue('location.location.label', '')
      resetReactHookFormAddressFields<OfferEducationalFormValues>(
        (name, defaultValue) => {
          setValue(name, defaultValue)
        }
      )
    } else {
      // If here, the user chose to use the venue address
      setVenueAddressFields()
    }
  }

  const onAddressSelect = (data: AdresseData) => {
    setValue('location.location.isVenueLocation', false)
    setValue('location.location.isManualEdition', false)
    setValue('street', data.address)
    setValue('postalCode', data.postalCode)
    setValue('city', data.city)
    setValue('latitude', data.latitude.toString())
    setValue('longitude', data.longitude.toString())
    setValue('banId', data.id)
    setValue('inseeCode', data.inseeCode)
    setValue('coords', `${data.latitude}, ${data.longitude}`)
  }

  const locationTypeRadios = [
    {
      label: 'À une adresse précise',
      value: CollectiveLocationType.ADDRESS,
      collapsed: (
        <RadioButtonGroup
          onChange={handleAddressLocationChange}
          disabled={disableForm}
          label="Type d'adresse"
          variant="detailed"
          checkedOption={watch('location.location.id')}
          name="location.location.id"
          options={[
            {
              label: selectedPartnerVenue
                ? `${selectedPartnerVenue.location?.label} - ${selectedPartnerVenue.location?.street}
                  ${selectedPartnerVenue.location?.postalCode} ${selectedPartnerVenue.location?.city}`
                : 'Adresse du lieu sélectionné',
              value: selectedPartnerVenue?.location?.id.toString() ?? '',
            },
            {
              label: 'Autre adresse',
              value: 'SPECIFIC_ADDRESS',
              collapsed: (
                <div className={styles['specific-address']}>
                  <TextInput
                    label="Intitulé de la localisation"
                    {...register('location.location.label')}
                    error={
                      getFieldState('location.location.label').error?.message
                    }
                    disabled={disableForm}
                  />
                  <AddressFields
                    addressRegister={register('addressAutocomplete')}
                    onAddressChosen={onAddressSelect}
                    renderManual={() => (
                      <AddressManual
                        gpsCalloutMessage={
                          'Les coordonnées GPS permettent aux enseignants de trouver votre offre sur ADAGE.'
                        }
                        readOnlyFields={
                          disableForm
                            ? ['city', 'street', 'postalCode', 'coords']
                            : []
                        }
                      />
                    )}
                    error={getFieldState('addressAutocomplete').error?.message}
                    disabled={disableForm}
                    className={styles['specific-address-search']}
                    manual={isManualEdition}
                    onManualChange={toggleManualAddressForm}
                  />
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
      const { location } = selectedPartnerVenue || {}
      // If here, the user chose to use the venue address
      setVenueAddressFields()
      setValue('location.location.id', location?.id.toString())
      setValue('location.locationType', CollectiveLocationType.ADDRESS)
      setValue('location.locationComment', '')
      setValue('interventionArea', [])
    } else {
      resetReactHookFormAddressFields<OfferEducationalFormValues>(
        (name, defaultValue) => setValue(name, defaultValue)
      )
    }

    setTimeout(() => {
      const el = radioGroupRef.current
      if (!el) {
        return
      }
      const rect = el.getBoundingClientRect()
      const isVisible =
        rect.top >= 0 &&
        rect.bottom <=
          (window.innerHeight || document.documentElement.clientHeight)
      if (!isVisible) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }, 0)
  }

  const radioGroupRef = useRef<HTMLDivElement>(null)

  return (
    <FormLayout.Row>
      <div ref={radioGroupRef}>
        <RadioButtonGroup
          onChange={handleLocationTypeChange}
          options={locationTypeRadios}
          variant="detailed"
          label={
            <h2 className={styles['radio-group-title']}>
              Où se déroule votre offre ?
            </h2>
          }
          name="location.locationType"
          disabled={disableForm}
          checkedOption={watch('location.locationType')}
        />
      </div>
    </FormLayout.Row>
  )
}
