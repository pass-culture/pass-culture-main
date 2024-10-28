import { useFormikContext } from 'formik'
import React from 'react'

import {
  GetOffererNameResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FormLayout } from 'components/FormLayout/FormLayout'
import {
  IndividualOfferForm,
  IndividualOfferFormValues,
} from 'pages/IndividualOffer/commons/types'
import { buildAccessibilityFormValues } from 'pages/IndividualOffer/IndividualOfferDetailsAndInformations/IndividualOfferInformationsLegacy/InformationsScreen/IndividualOfferForm/commons/utils/setDefaultInitialFormValues'
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
          onChange={(event) =>
            onVenueChange(setFieldValue, venueList, event.target.value)
          }
        />
      </FormLayout.Row>
    </>
  )
}
