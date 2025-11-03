import type { RootState } from '@/commons/store/store'

export const selectMusicTypes = (state: RootState) => state.musicTypes.list
