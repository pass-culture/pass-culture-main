import { useDispatch, useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from '@/apiClient/api'

import { GET_MUSIC_TYPES_QUERY_KEY } from '../config/swrQueryKeys'
import { updateMusicTypes } from '../store/staticData/reducer'
import { selectMusicTypes } from '../store/staticData/selectors'

export function useMusicTypes() {
  const dispatch = useDispatch()
  const musicTypes = useSelector(selectMusicTypes)
  const shouldFetchMusicTypes = musicTypes === undefined

  const { data } = useSWR(
    () => {
      return shouldFetchMusicTypes ? GET_MUSIC_TYPES_QUERY_KEY : null
    },
    async () => {
      const response = await api.getMusicTypes()
      dispatch(updateMusicTypes(response))
      return response
    },
    { fallbackData: [] }
  )
  return { musicTypes: musicTypes || data }
}
