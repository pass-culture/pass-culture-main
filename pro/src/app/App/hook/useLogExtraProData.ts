import { useEffect, useState } from 'react'
import { useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'

export const useLogExtraProData = (): void => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const [previousOfferer, setPreviousOfferer] = useState<number>()
  const [previousVenue, setPreviousVenue] = useState<number>()
  const selectedOffererId = useAppSelector(selectCurrentOffererId)
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

  const selectedVenue = useAppSelector((state) => state.user.selectedVenue)

  useEffect(() => {
    if (
      withSwitchVenueFeature &&
      selectedVenue &&
      selectedOffererId &&
      (selectedVenue.id !== previousVenue ||
        selectedOffererId !== previousOfferer)
    ) {
      logEvent(Events.EXTRA_PRO_DATA, {
        offerer_id: selectedOffererId,
        venue_id: selectedVenue.id,
        from: location.pathname,
      })

      setPreviousOfferer(selectedOffererId)
      setPreviousVenue(selectedVenue.id)
    } else if (selectedOffererId && selectedOffererId !== previousOfferer) {
      logEvent(Events.EXTRA_PRO_DATA, {
        offerer_id: selectedOffererId,
        from: location.pathname,
      })

      setPreviousOfferer(selectedOffererId)
    }
  }, [
    selectedOffererId,
    logEvent,
    location.pathname,
    previousOfferer,
    selectedVenue?.id,
    withSwitchVenueFeature,
  ])
}
