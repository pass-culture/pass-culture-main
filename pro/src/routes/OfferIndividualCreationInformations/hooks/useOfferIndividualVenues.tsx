import React, { useEffect, useState } from 'react'

import { getOfferIndividualVenuesAdapter } from 'core/Venue/adapters'
import { TOfferIndividualVenue } from 'core/Venue/types'

const useOfferIndividualVenues = (): {
  isLoading: boolean
  offerIndividualVenues: TOfferIndividualVenue[]
  error: string
} => {
  const [offerIndividualVenues, setOfferIndividualVenues] = useState<
    TOfferIndividualVenue[]
  >([])
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState<boolean>(true)
  useEffect(() => {
    async function loadData() {
      const response = await getOfferIndividualVenuesAdapter()
      if (response.isOk) {
        setOfferIndividualVenues(response.payload)
      } else {
        setError(response.message)
      }

      setIsLoading(false)
    }
    if (isLoading) {
      loadData()
    }
  }, [isLoading])

  return { isLoading, offerIndividualVenues, error }
}

export default useOfferIndividualVenues
