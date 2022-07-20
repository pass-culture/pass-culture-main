import { buildOffererOptions, buildVenueOptions } from './utils'

import FormLayout from 'new_components/FormLayout'
import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'
import React from 'react'
import { Select } from 'ui-kit'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { TOffererName } from 'core/Offerers/types'
import { useFormikContext } from 'formik'
import { useVenueUpdates } from './hooks'

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
