import { useEffect, useState } from 'react'
import { useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'

export const useLogExtraProData = (): void => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const [previousOfferer, setPreviousOfferer] = useState<number>()
  const selectedOffererId = useAppSelector(selectCurrentOffererId)

  // TODO: AmineL rajouter le venue_id quand il y aura le switch structure
  useEffect(() => {
    if (selectedOffererId && selectedOffererId !== previousOfferer) {
      logEvent(Events.EXTRA_PRO_DATA, {
        offerer_id: selectedOffererId,
        from: location.pathname,
      })

      setPreviousOfferer(selectedOffererId)
    }
  }, [selectedOffererId, logEvent, location.pathname, previousOfferer])
}
