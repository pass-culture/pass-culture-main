import { useFormikContext } from 'formik'
import React from 'react'

import {
  GetOffererNameResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OFFER_LOCATION } from 'components/IndividualOfferForm/OfferLocation/constants'
import {
  IndividualOfferForm,
  IndividualOfferFormValues,
} from 'components/IndividualOfferForm/types'
import { resetAddressFields } from 'components/IndividualOfferForm/utils/resetAddressFields'
import { buildAccessibilityFormValues } from 'components/IndividualOfferForm/utils/setDefaultInitialFormValues'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { Select } from 'ui-kit/form/Select/Select'

import { buildOffererOptions, buildVenueOptions } from './utils'

export interface VenueProps {
  offererNames: GetOffererNameResponseModel[]
  venueList: VenueListItemResponseModel[]
  hideOfferer?: boolean
  readOnlyFields?: string[]
}

export const onVenueChange = async (
  setFieldValue: IndividualOfferForm['setFieldValue'],
  venueList: VenueListItemResponseModel[],
  venueId: string
) => {
  const newVenue = venueList.find((v) => v.id.toString() === venueId)

  if (!newVenue) {
    return
  }
  await setFieldValue('isVenueVirtual', newVenue.isVirtual)
  await setFieldValue('withdrawalDetails', newVenue.withdrawalDetails || '')
  await setFieldValue('accessibility', buildAccessibilityFormValues(newVenue))
}

export const Venue = ({
  offererNames,
  venueList,
  hideOfferer = false,
  readOnlyFields = [],
}: VenueProps): JSX.Element => {
  const formik = useFormikContext<IndividualOfferFormValues>()
  const { values, setFieldValue } = formik
  const { isDisabled: isOffererDisabled, offererOptions } =
    buildOffererOptions(offererNames)

  const { isDisabled: isVenueDisabled, venueOptions } = buildVenueOptions(
    values.offererId ?? '',
    venueList
  )

  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')
  if (!isOfferAddressEnabled) {
    venueOptions.unshift({ label: 'Sélectionner un lieu', value: '' })
  }

  const onOffererChange = async (
    event: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const { venueOptions: newVenueOptions } = buildVenueOptions(
      event.target.value,
      venueList
    )
    if (newVenueOptions.length === 1) {
      await setFieldValue('venueId', newVenueOptions[0].value)
      await onVenueChange(
        setFieldValue,
        venueList,
        String(newVenueOptions[0].value)
      )
    }
  }

  const onSelectVenueChange = async (
    event: React.ChangeEvent<HTMLSelectElement>
  ) => {
    if (
      isOfferAddressEnabled &&
      values.offerlocation !== OFFER_LOCATION.OTHER_ADDRESS
    ) {
      await Promise.all([
        resetAddressFields({ formik }),
        setFieldValue('offerlocation', ''),
      ])
    }
    await onVenueChange(setFieldValue, venueList, event.target.value)
  }

  return (
    <>
      {!hideOfferer && (
        <FormLayout.Row>
          <Select
            disabled={isOffererDisabled || readOnlyFields.includes('offererId')}
            label="Structure"
            name="offererId"
            options={offererOptions}
            onChange={onOffererChange}
          />
        </FormLayout.Row>
      )}
      <FormLayout.Row>
        <Select
          disabled={isVenueDisabled || readOnlyFields.includes('venueId')}
          label={isOfferAddressEnabled ? `Qui propose l’offre ?` : 'Lieu'}
          name="venueId"
          options={venueOptions}
          onChange={onSelectVenueChange}
        />
      </FormLayout.Row>
    </>
  )
}
