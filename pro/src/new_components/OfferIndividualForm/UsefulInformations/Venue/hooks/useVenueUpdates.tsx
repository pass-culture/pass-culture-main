import { useFormikContext } from 'formik'
import { useEffect, useState } from 'react'

import { TOfferIndividualVenue } from 'core/Venue/types'
import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm/types'

const useVenueUpdates = (venueList: TOfferIndividualVenue[]): void => {
  const {
    values: { venueId },
    setFieldValue,
  } = useFormikContext<IOfferIndividualFormValues>()
  const [prevValue, setPrevValue] =
    useState<IOfferIndividualFormValues['venueId']>(venueId)

  useEffect(() => {
    if (venueId !== prevValue) {
      const venue = venueList.find(v => v.id === venueId)

      // update offer accessibility from venue when venue accessibility is defined.
      venue &&
        Object.values(venue.accessibility).includes(true) &&
        setFieldValue('accessibility', venue.accessibility)
      setPrevValue(venueId)
    }
  }, [venueId, prevValue, setFieldValue])
}

export default useVenueUpdates
