import { useEffect, useState } from 'react'
import { useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'

// TODO (igabriele, 2026-03-31): Remove this hook and integrate its logic directly within dispatchers + Check adpatation for WIP_SWITCH_VENUE FF with data team.
export const useLogExtraProData = (): void => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const [previousOfferer, setPreviousOfferer] = useState<number>()
  const [previousVenue, setPreviousVenue] = useState<number>()

  const selectedPartnerVenue = useAppSelector(
    (state) => state.user.selectedPartnerVenue
  )
  const selectedOffererId = selectedPartnerVenue?.managingOfferer.id

  useEffect(() => {
    if (
      selectedPartnerVenue &&
      selectedOffererId &&
      (selectedPartnerVenue.id !== previousVenue ||
        selectedOffererId !== previousOfferer)
    ) {
      logEvent(Events.EXTRA_PRO_DATA, {
        offerer_id: selectedOffererId,
        venue_id: selectedPartnerVenue.id,
        from: location.pathname,
      })

      setPreviousOfferer(selectedOffererId)
      setPreviousVenue(selectedPartnerVenue.id)
    }
  }, [
    selectedOffererId,
    selectedPartnerVenue,
    logEvent,
    location.pathname,
    previousOfferer,
    previousVenue,
    selectedPartnerVenue?.id,
  ])
}
