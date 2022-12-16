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
        setFieldValue('isVenueVirtual', venue.isVirtual)
        setFieldValue('withdrawalDetails', venue?.withdrawalDetails || '')

        // update offer accessibility from venue when venue accessibility is defined.
        // set accessibility value after isVenueVirtual and withdrawalDetails otherwise the error message doesn't hide
        Object.values(venue.accessibility).includes(true) &&
          setFieldValue('accessibility', venue.accessibility)
      }
      setPrevValue(venueId)
    }
  }, [venueId, prevValue, setFieldValue])
}

export default useVenueUpdates
