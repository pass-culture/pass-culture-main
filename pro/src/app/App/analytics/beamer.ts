import { useEffect } from 'react'
import { useLocation } from 'react-router'

import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentUser } from '@/commons/store/user/selectors'

export const useBeamer = (consentedToBeamer: boolean) => {
  const isBeamerEnabled = useActiveFeature('ENABLE_BEAMER')
  const currentUser = useAppSelector(selectCurrentUser)
  const location = useLocation()

  useEffect(() => {
    if (
      isBeamerEnabled &&
      consentedToBeamer &&
      currentUser !== null &&
      window.Beamer !== undefined &&
      location.pathname.indexOf('/inscription/structure') === -1
    ) {
      // We use setTimeout because Beamer might not be loaded yet
      setTimeout(() => {
        window.Beamer?.update({
          user_id: currentUser.id.toString(),
          departmentCode: currentUser.departementCode,
        })
        window.Beamer?.init()
      }, 1000)
    } else {
      window.Beamer?.destroy()
    }
  }, [currentUser, consentedToBeamer, isBeamerEnabled, location])
}
