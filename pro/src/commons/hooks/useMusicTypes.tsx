import useSWR from 'swr'

import { api } from '@/apiClient/api'

import { GET_MUSIC_TYPES_QUERY_KEY } from '../config/swrQueryKeys'
import { updateMusicTypes } from '../store/staticData/reducer'
import { selectMusicTypes } from '../store/staticData/selectors'
import { useAppDispatch } from './useAppDispatch'
import { useAppSelector } from './useAppSelector'

export function useMusicTypes() {
  const dispatch = useAppDispatch()
  const musicTypes = useAppSelector(selectMusicTypes)
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
