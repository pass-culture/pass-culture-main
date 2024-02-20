import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import { updateFeatures } from 'store/features/reducer'
import { selectLastLoaded } from 'store/features/selectors'
import { sendSentryCustomError } from 'utils/sendSentryCustomError'

const THIRTY_MINUTES = 1000 * 60 * 30

export function useLoadFeatureFlags() {
  const dispatch = useDispatch()
  const lastLoaded = useSelector(selectLastLoaded)
  const { pathname } = useLocation()

  useEffect(() => {
    const loadFeatures = async () => {
      try {
        const response = await api.listFeatures()
        dispatch(updateFeatures(response))
      } catch (e) {
        sendSentryCustomError(e)
      }
    }
    if (!lastLoaded || lastLoaded < Date.now() - THIRTY_MINUTES) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      loadFeatures()
    }
  }, [dispatch, pathname, lastLoaded])
}
