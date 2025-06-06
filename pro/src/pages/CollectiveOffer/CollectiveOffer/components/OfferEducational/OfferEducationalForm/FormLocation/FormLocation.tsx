import { useId, useState } from 'react'
import { useFormContext } from 'react-hook-form'

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
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { AddressManual } from 'ui-kit/formV2/AddressManual/AddressManual'
import { AddressSelect } from 'ui-kit/formV2/AddressSelect/AddressSelect'
import { RadioGroup } from 'ui-kit/formV2/RadioGroup/RadioGroup'
import { TextArea } from 'ui-kit/formV2/TextArea/TextArea'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

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
  const specificAddressId = useId()
  const { watch, setValue, resetField, register, getFieldState } =
    useFormContext<OfferEducationalFormValues>()
  const [shouldShowManualAddressForm, setShouldShowManualAddressForm] =
    useState(watch('location.address')?.isManualEdition)

  const selectedVenue = venues.find((v) => v.id.toString() === watch('venueId'))

  const toggleManualAddressForm = () => {
    setShouldShowManualAddressForm(!shouldShowManualAddressForm)
    if (!shouldShowManualAddressForm) {
      setValue('location.address.isVenueAddress', false)
      setValue('location.address.isManualEdition', true)
      resetReactHookFormAddressFields({ resetField })
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
    const isSpecificAddress = event.target.value === 'SPECIFIC_ADDRESS'

    if (isSpecificAddress) {
      setValue('location.address.label', '')
      resetReactHookFormAddressFields({ resetField })
    } else {
      // If here, the user chose to use the venue address
      setVenueAddressFields()
    }
  }

  const onAddressSelect = () => {
    setValue('location.address.isVenueAddress', false)
    setValue('location.address.isManualEdition', false)
  }

  const locationTypeRadios = [
    {
      label: <span id={specificAddressId}>À une adresse précise</span>,
      value: CollectiveLocationType.ADDRESS,
      childrenOnChecked: (
        <RadioGroup
          describedBy={specificAddressId}
          onChange={handleAddressLocationChange}
          variant={RadioVariant.BOX}
          disabled={disableForm}
          group={[
            {
              label: (
                <span>
                  {selectedVenue &&
                    `${selectedVenue.address?.label} - ${selectedVenue.address?.street}
                  ${selectedVenue.address?.postalCode} ${selectedVenue.address?.city}`}
                </span>
              ),
              value: selectedVenue?.address?.id_oa.toString() ?? '',
            },
            {
              label: 'Autre adresse',
              value: 'SPECIFIC_ADDRESS',
              childrenOnChecked: (
                <>
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
                </>
              ),
            },
          ]}
          name={'location.address.id_oa'}
        />
      ),
    },
    {
      label: 'En établissement scolaire',
      value: CollectiveLocationType.SCHOOL,
      childrenOnChecked: (
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
      childrenOnChecked: (
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
    if (event.target.value === CollectiveLocationType.ADDRESS) {
      const { address } = selectedVenue || {}
      // If here, the user chose to use the venue address
      setVenueAddressFields()
      setValue('location.address.id_oa', address?.id_oa.toString())
      setValue('location.locationType', CollectiveLocationType.ADDRESS)
      setValue('location.locationComment', '')
      setValue('interventionArea', [])
    } else {
      resetReactHookFormAddressFields({ resetField })
    }
  }

  return (
    <FormLayout.Row>
      <RadioGroup
        onChange={handleLocationTypeChange}
        group={locationTypeRadios}
        legend={
          <h2 className={styles['subtitle']}>Où se déroule votre offre ? *</h2>
        }
        name="location.locationType"
        variant={RadioVariant.BOX}
        disabled={disableForm}
      />
    </FormLayout.Row>
  )
}
