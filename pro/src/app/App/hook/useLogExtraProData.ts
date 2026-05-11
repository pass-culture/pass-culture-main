import { useEffect, useState } from 'react'
import { useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'

// TODO (igabriele, 2026-03-31): Remove this hook and integrate its logic directly within dispatchers + Check adaptation for WIP_SWITCH_VENUE FF with data team.
export const useLogExtraProData = (): void => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const [previousVenue, setPreviousVenue] = useState<number>()

  const selectedPartnerVenue = useAppSelector(
    (state) => state.user.selectedPartnerVenue
  )

  useEffect(() => {
    if (selectedPartnerVenue && selectedPartnerVenue.id !== previousVenue) {
      logEvent(Events.EXTRA_PRO_DATA, {
        offerer_id: selectedPartnerVenue.managingOfferer.id,
        venue_id: selectedPartnerVenue.id,
        from: location.pathname,
      })

      setPreviousVenue(selectedPartnerVenue.id)
    }
  }, [selectedPartnerVenue, logEvent, location.pathname, previousVenue])
}
