import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { IOfferIndividualFormValues } from 'components/OfferIndividualForm'
import { OfferIndividualForm } from 'components/OfferIndividualForm/types'
import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { Select } from 'ui-kit'

import { buildOffererOptions, buildVenueOptions } from './utils'

export interface IVenueProps {
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
  readOnlyFields?: string[]
}

export const onVenueChange = (
  setFieldValue: OfferIndividualForm['setFieldValue'],
  venueList: TOfferIndividualVenue[],
  venueId: string
) => {
  const newVenue = venueList.find(v => v.nonHumanizedId.toString() === venueId)

  if (!newVenue) {
    return
  }
  setFieldValue('isVenueVirtual', newVenue.isVirtual)
  setFieldValue('withdrawalDetails', newVenue?.withdrawalDetails || '')

  // update offer accessibility from venue when venue accessibility is defined.
  // set accessibility value after isVenueVirtual and withdrawalDetails otherwise the error message doesn't hide
  Object.values(newVenue.accessibility).includes(true) &&
    setFieldValue('accessibility', newVenue.accessibility)
}

const Venue = ({
  offererNames,
  venueList,
  readOnlyFields = [],
}: IVenueProps): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<IOfferIndividualFormValues>()
  const { isDisabled: isOffererDisabled, offererOptions } =
    buildOffererOptions(offererNames)

  const { isDisabled: isVenueDisabled, venueOptions } = buildVenueOptions(
    values.offererId,
    venueList
  )

  const onOffererChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const { venueOptions: newVenueOptions } = buildVenueOptions(
      event.target.value,
      venueList
    )
    if (newVenueOptions.length === 1) {
      setFieldValue('venueId', newVenueOptions[0].value)
      onVenueChange(setFieldValue, venueList, String(newVenueOptions[0].value))
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
          onChange={event =>
            onVenueChange(setFieldValue, venueList, event.target.value)
          }
        />
      </FormLayout.Row>
    </>
  )
}

export default Venue
