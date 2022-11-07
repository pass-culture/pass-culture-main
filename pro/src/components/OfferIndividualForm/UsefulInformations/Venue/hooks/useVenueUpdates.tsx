import { useFormikContext } from 'formik'
import { useEffect, useState } from 'react'

import { IOfferIndividualFormValues } from 'components/OfferIndividualForm/types'
import { TOfferIndividualVenue } from 'core/Venue/types'

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

      if (venue) {
        // update offer accessibility from venue when venue accessibility is defined.
        Object.values(venue.accessibility).includes(true) &&
          setFieldValue('accessibility', venue.accessibility)

        setFieldValue('isVenueVirtual', venue.isVirtual)
      }
      setPrevValue(venueId)
    }
  }, [venueId, prevValue, setFieldValue])
}

export default useVenueUpdates
