import { AdagePlaylistType } from '@/apiClient/adage'

export type PlaylistTracker = {
  playlistId: number
  playlistType: AdagePlaylistType
  index?: number
  offerId?: number
  venueId?: number
  domainId?: number
}

export type OfferPlaylistTracker = PlaylistTracker & { offerId: number }

export type VenuePlaylistTracker = PlaylistTracker & { venueId: number }
