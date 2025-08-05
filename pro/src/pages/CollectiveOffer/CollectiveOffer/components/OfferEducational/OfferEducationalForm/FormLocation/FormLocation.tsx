import { AdresseData } from 'apiClient/adresse/types'
import {
  CollectiveLocationType,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { resetReactHookFormAddressFields } from 'commons/utils/resetAddressFields'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { RadioButtonGroup } from 'design-system/RadioButtonGroup/RadioButtonGroup'
import fullBackIcon from 'icons/full-back.svg'
import fullNextIcon from 'icons/full-next.svg'
import { useRef } from 'react'
import { useFormContext } from 'react-hook-form'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { AddressManual } from 'ui-kit/form/AddressManual/AddressManual'
import { AddressSelect } from 'ui-kit/form/AddressSelect/AddressSelect'
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
  const isManualEdition = watch('location.address.isManualEdition')

  const selectedVenue = venues.find((v) => v.id.toString() === watch('venueId'))

  const toggleManualAddressForm = () => {
    setValue('location.address.isManualEdition', !isManualEdition)
    if (!isManualEdition) {
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
          checkedOption={watch('location.address.id_oa')}
          name="location.address.id_oa"
          options={[
            {
              label: selectedVenue
                ? `${selectedVenue.address?.label} - ${selectedVenue.address?.street}
                  ${selectedVenue.address?.postalCode} ${selectedVenue.address?.city}`
                : 'Adresse du lieu sélectionné',
              value: selectedVenue?.address?.id_oa.toString() ?? '',
            },
            {
              label: 'Autre adresse',
              value: 'SPECIFIC_ADDRESS',
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
                    disabled={disableForm || isManualEdition}
                    onAddressChosen={onAddressSelect}
                    label="Adresse postale"
                    {...register('addressAutocomplete')}
                    className={styles['specific-address-search']}
                    error={
                      !disableForm && !isManualEdition
                        ? getFieldState('addressAutocomplete').error?.message
                        : undefined
                    }
                  />
                  <Button
                    variant={ButtonVariant.QUATERNARY}
                    icon={isManualEdition ? fullBackIcon : fullNextIcon}
                    onClick={toggleManualAddressForm}
                    disabled={disableForm}
                  >
                    {isManualEdition ? (
                      <>Revenir à la sélection automatique</>
                    ) : (
                      <>Vous ne trouvez pas votre adresse ?</>
                    )}
                  </Button>
                  {isManualEdition && (
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
          required
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
          label="Où se déroule votre offre ?"
          labelTag="h2"
          name="location.locationType"
          disabled={disableForm}
          checkedOption={watch('location.locationType')}
          required
        />
      </div>
    </FormLayout.Row>
  )
}
