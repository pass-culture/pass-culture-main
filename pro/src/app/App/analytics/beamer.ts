import { useEffect } from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import { useActiveFeature } from 'hooks/useActiveFeature'
import { selectCurrentUser } from 'store/user/selectors'

export const useBeamer = (consentedToBeamer: boolean) => {
  const isBeamerEnabled = useActiveFeature('ENABLE_BEAMER')
  const currentUser = useSelector(selectCurrentUser)
  const location = useLocation()

  useEffect(() => {
    if (
      isBeamerEnabled &&
      consentedToBeamer &&
      currentUser !== null &&
      window.Beamer !== undefined &&
      location.pathname.indexOf('/parcours-inscription') === -1
    ) {
      // We use setTimeout because Beamer might not be loaded yet
      setTimeout(() => {
        window.Beamer?.update({ user_id: currentUser.id.toString() })
        window.Beamer?.init()
      }, 1000)
    } else {
      window.Beamer?.destroy()
    }
  }, [currentUser, consentedToBeamer, isBeamerEnabled, location])
}
