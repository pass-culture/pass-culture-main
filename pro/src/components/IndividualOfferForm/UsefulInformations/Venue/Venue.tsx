import { useFormikContext } from 'formik'
import React from 'react'

import { GetOffererNameResponseModel } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { IndividualOfferFormValues } from 'components/IndividualOfferForm'
import { IndividualOfferForm } from 'components/IndividualOfferForm/types'
import { buildAccessibilityFormValues } from 'components/VenueForm/utils/setInitialFormValues'
import { IndividualOfferVenueItem } from 'core/Venue/types'
import { Select } from 'ui-kit'

import { buildOffererOptions, buildVenueOptions } from './utils'

export interface VenueProps {
  offererNames: GetOffererNameResponseModel[]
  venueList: IndividualOfferVenueItem[]
  readOnlyFields?: string[]
}

export const onVenueChange = async (
  setFieldValue: IndividualOfferForm['setFieldValue'],
  venueList: IndividualOfferVenueItem[],
  venueId: string
) => {
  const newVenue = venueList.find((v) => v.id.toString() === venueId)

  if (!newVenue) {
    return
  }
  await setFieldValue('isVenueVirtual', newVenue.isVirtual)
  await setFieldValue('withdrawalDetails', newVenue?.withdrawalDetails || '')
  await setFieldValue('accessibility', buildAccessibilityFormValues(newVenue))
}

const Venue = ({
  offererNames,
  venueList,
  readOnlyFields = [],
}: VenueProps): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<IndividualOfferFormValues>()
  const { isDisabled: isOffererDisabled, offererOptions } =
    buildOffererOptions(offererNames)

  const { isDisabled: isVenueDisabled, venueOptions } = buildVenueOptions(
    values.offererId ?? '',
    venueList
  )

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
      <FormLayout.Row>
        <Select
          disabled={isOffererDisabled || readOnlyFields.includes('offererId')}
          label="Structure"
          name="offererId"
          options={offererOptions}
          onChange={onOffererChange}
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <Select
          disabled={isVenueDisabled || readOnlyFields.includes('venueId')}
          label="Lieu"
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

export default Venue
