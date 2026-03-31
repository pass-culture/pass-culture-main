import { useEffect, useState } from 'react'
import { useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'

// TODO (igabriele, 2026-03-31): Remove this hook and integrate its logic directly within dispatchers + Check adpatation for WIP_SWITCH_VENUE FF with data team.
export const useLogExtraProData = (): void => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const [previousOfferer, setPreviousOfferer] = useState<number>()
  const [previousVenue, setPreviousVenue] = useState<number>()
  const selectedOffererId = useAppSelector(selectCurrentOffererId)
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

  const selectedPartnerVenue = useAppSelector(
    (state) => state.user.selectedPartnerVenue
  )

  useEffect(() => {
    if (
      withSwitchVenueFeature &&
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
    } else if (selectedOffererId && selectedOffererId !== previousOfferer) {
      logEvent(Events.EXTRA_PRO_DATA, {
        offerer_id: selectedOffererId,
        from: location.pathname,
      })

      setPreviousOfferer(selectedOffererId)
    }
  }, [
    selectedOffererId,
    selectedPartnerVenue,
    logEvent,
    location.pathname,
    previousOfferer,
    previousVenue,
    selectedPartnerVenue?.id,
    withSwitchVenueFeature,
  ])
}
