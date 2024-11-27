import { AdagePlaylistType } from 'apiClient/adage'

export type TrackerElementArg = {
  playlistId: number
  playlistType: AdagePlaylistType
  elementId?: number
  index?: number
}
