import { useFormikContext } from 'formik'
import React from 'react'

import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import FormLayout from 'new_components/FormLayout'
import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'
import { Select } from 'ui-kit'

import { useVenueUpdates } from './hooks'
import { buildOffererOptions, buildVenueOptions } from './utils'

export interface IVenueProps {
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
}

const Venue = ({ offererNames, venueList }: IVenueProps): JSX.Element => {
  const { values } = useFormikContext<IOfferIndividualFormValues>()
  const { isDisabled: isOffererDisabled, offererOptions } =
    buildOffererOptions(offererNames)

  const { isDisabled: isVenueDisabled, venueOptions } = buildVenueOptions(
    values.offererId,
    venueList
  )

  useVenueUpdates(venueList)

  return (
    <>
      <FormLayout.Row>
        <Select
          disabled={isOffererDisabled}
          label="Structure"
          name="offererId"
          options={offererOptions}
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <Select
          disabled={isVenueDisabled}
          label="Lieu"
          name="venueId"
          options={venueOptions}
        />
      </FormLayout.Row>
    </>
  )
}

export default Venue
