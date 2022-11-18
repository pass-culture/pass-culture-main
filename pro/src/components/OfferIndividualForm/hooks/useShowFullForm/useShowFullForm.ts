import { useEffect, useState } from 'react'

import { TOfferIndividualVenue } from 'core/Venue/types'

const useShowFullForm = (
  subcategoryId: string,
  filteredVenueList: TOfferIndividualVenue[]
): boolean => {
  const [showFullForm, setShowFullForm] = useState<boolean>(false)
  useEffect(() => {
    setShowFullForm(subcategoryId.length > 0 && filteredVenueList.length > 0)
  }, [subcategoryId, filteredVenueList])

  return showFullForm
}
export default useShowFullForm
