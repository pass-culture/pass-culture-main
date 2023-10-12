import { useEffect, useState } from 'react'

import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getFilteredBookingsRecapAdapter } from 'pages/Bookings/adapters'

export const useOfferBookingsCount = (
  mode: OFFER_WIZARD_MODE,
  offerId?: number
) => {
  const [bookingsCount, setBookingsCount] = useState<number>(0)
  const [isLoading, setIsLoading] = useState<boolean>(false)

  useEffect(() => {
    const loadBookings = async () => {
      if (!offerId || mode === OFFER_WIZARD_MODE.CREATION) {
        return
      }

      setIsLoading(true)
      const response = await getFilteredBookingsRecapAdapter({
        ...DEFAULT_PRE_FILTERS,
        offerId: String(offerId),
      })

      if (response.isOk) {
        setBookingsCount(response.payload.total)
      }
      setIsLoading(false)
    }
    loadBookings()
  }, [offerId, mode])

  return { bookingsCount, isLoading }
}
