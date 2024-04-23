import { useDispatch, useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GET_FEATURES_QUERY_KEY } from 'config/swrQueryKeys'
import { updateFeatures } from 'store/features/reducer'
import { selectLastLoaded } from 'store/features/selectors'

const THIRTY_MINUTES = 1000 * 60 * 30

export function useLoadFeatureFlags() {
  const dispatch = useDispatch()
  const lastLoaded = useSelector(selectLastLoaded)
  const { pathname } = useLocation()

  useSWR(
    () => {
      const areFeaturesUpToDate =
        lastLoaded && lastLoaded >= Date.now() - THIRTY_MINUTES

      return areFeaturesUpToDate ? null : [GET_FEATURES_QUERY_KEY, pathname]
    },
    async () => {
      const response = await api.listFeatures()
      dispatch(updateFeatures(response))
    }
  )
}
