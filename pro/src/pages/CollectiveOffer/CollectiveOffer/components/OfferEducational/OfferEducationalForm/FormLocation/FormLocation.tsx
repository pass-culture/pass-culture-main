import { useFormikContext } from 'formik'
import { useCallback, useId, useState } from 'react'

import {
  CollectiveLocationType,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { offerInterventionOptions } from 'commons/core/shared/interventionOptions'
import { interventionAreaMultiSelect } from 'commons/utils/interventionAreaMultiSelect'
import { resetAddressFields } from 'commons/utils/resetAddressFields'
import { AddressSelect } from 'components/Address/Address'
import { AddressManual } from 'components/AddressManual/AddressManual'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullBackIcon from 'icons/full-back.svg'
import fullNextIcon from 'icons/full-next.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { MultiSelect, Option } from 'ui-kit/MultiSelect/MultiSelect'

import styles from '../OfferEducationalForm.module.scss'
export interface FormLocationProps {
  disableForm: boolean
  venues: VenueListItemResponseModel[]
}

export const FormLocation = ({
  venues,
  disableForm,
}: FormLocationProps): JSX.Element => {
  const specificAddressId = useId()
  const radioInstitutionId = useId()
  const formik = useFormikContext<OfferEducationalFormValues>()
  const setFieldValue = formik.setFieldValue
  const [shouldShowManualAddressForm, setShouldShowManualAddressForm] =
    useState(formik.values.location.address.isManualEdition)

  const selectedVenue = venues.find(
    (v) => v.id.toString() === formik.values.venueId.toString()
  )

  const toggleManualAddressForm = async () => {
    setShouldShowManualAddressForm(!shouldShowManualAddressForm)
    if (!shouldShowManualAddressForm) {
      await setFieldValue('location.address.isVenueAddress', false)
      await setFieldValue('location.address.isManualEdition', true)
      await resetAddressFields({ formik })
    }
  }

  const setVenueAddressFields = async () => {
    const { address } = selectedVenue || {}
    await Promise.all([
      setFieldValue('banId', address?.banId),
      setFieldValue('city', address?.city),
      setFieldValue('longitude', address?.longitude),
      setFieldValue('latitude', address?.latitude),
      setFieldValue('postalCode', address?.postalCode),
      setFieldValue('street', address?.street),
      setFieldValue('location.address.inseeCode', address?.inseeCode),
      setFieldValue('location.address.label', address?.label),
      setFieldValue('location.address.isVenueAddress', true),
      setFieldValue('location.address.isManualEdition', false),
    ])
  }

  const handleAddressLocationChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const isSpecificAddress = event.target.value === 'SPECIFIC_ADDRESS'

    if (isSpecificAddress) {
      await setFieldValue('location.address.label', '')
      await resetAddressFields({ formik })
    } else {
      // If here, the user chose to use the venue address
      await setVenueAddressFields()
    }
  }

  const onAddressSelect = async () => {
    await setFieldValue('location.address.isVenueAddress', false)
    await setFieldValue('location.address.isManualEdition', false)
  }

  const handleInterventionAreaChange = useCallback(
    (
      selectedOption: Option[],
      addedOptions: Option[],
      removedOptions: Option[]
    ) => {
      const newSelectedOptions = interventionAreaMultiSelect({
        selectedOption,
        addedOptions,
        removedOptions,
      })
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      setFieldValue('interventionArea', Array.from(newSelectedOptions))
    },
    [setFieldValue]
  )

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
                    name="location.address.label"
                    isOptional
                    disabled={disableForm}
                  />
                  <AddressSelect
                    disabled={disableForm || shouldShowManualAddressForm}
                    onAddressSelect={onAddressSelect}
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
      label: <span id={radioInstitutionId}>En établissement scolaire</span>,
      value: CollectiveLocationType.SCHOOL,
      childrenOnChecked: (
        <MultiSelect
          label="Indiquez aux enseignants les départements dans lesquels vous
            proposez votre offre."
          required
          name="interventionArea"
          buttonLabel="Département(s)"
          options={offerInterventionOptions}
          selectedOptions={offerInterventionOptions.filter((op) =>
            formik.values.interventionArea.includes(op.id)
          )}
          defaultOptions={offerInterventionOptions.filter((option) =>
            formik.values.interventionArea.includes(option.id)
          )}
          disabled={disableForm}
          hasSearch
          searchLabel="Rechercher un département"
          hasSelectAllOptions
          onSelectedOptionsChanged={handleInterventionAreaChange}
          onBlur={() => formik.setFieldTouched('interventionArea', true)}
          error={
            formik.touched.interventionArea && formik.errors.interventionArea
              ? String(formik.errors.interventionArea)
              : undefined
          }
          className={styles['intervention-area']}
        />
      ),
    },
  ]

  const handleLocationTypeChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (event.target.value === CollectiveLocationType.ADDRESS) {
      const { address } = selectedVenue || {}
      // If here, the user chose to use the venue address
      await setVenueAddressFields()
      await Promise.all([
        setFieldValue('location.address.id_oa', address?.id_oa.toString()),
        setFieldValue('location.locationType', CollectiveLocationType.ADDRESS),
        setFieldValue('interventionArea', []),
      ])
    } else {
      await resetAddressFields({ formik })
    }
  }

  return (
    <FormLayout.Row>
      <RadioGroup
        onChange={handleLocationTypeChange}
        group={locationTypeRadios}
        legend={
          <h2 className={styles['subtitle']}>Où se déroule votre offre ?</h2>
        }
        name="location.locationType"
        variant={RadioVariant.BOX}
        disabled={disableForm}
      />
    </FormLayout.Row>
  )
}
