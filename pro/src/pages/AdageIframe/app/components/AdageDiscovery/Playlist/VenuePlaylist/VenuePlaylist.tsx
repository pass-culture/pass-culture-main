import classNames from 'classnames'
import useSWR from 'swr'

import { AdagePlaylistType } from 'apiClient/adage/models/AdagePlaylistType'
import { apiAdage } from 'apiClient/api'
import { GET_LOCAL_OFFERERS_PLAYLIST_QUERY_KEY } from 'config/swrQueryKeys'

import { TrackerElementArg } from '../../AdageDiscovery'
import { Carousel } from '../../Carousel/Carousel'
import { VENUE_PLAYLIST } from '../../constant'
import VenueCard from '../../VenueCard/VenueCard'

import styles from './VenuePlaylist.module.scss'

type VenuePlaylistProps = {
  onWholePlaylistSeen: ({ playlistId, playlistType }: TrackerElementArg) => void
  trackPlaylistElementClicked: ({
    playlistId,
    playlistType,
    elementId,
    index,
  }: TrackerElementArg) => void
}

function getPlaylistTitle(distanceMax: number) {
  if (distanceMax <= 3) {
    return 'À moins de 30 minutes à pieds de mon établissement'
  }
  if (distanceMax <= 15) {
    return 'À environ 30 minutes de transport de mon établissement'
  }
  return 'À environ 1h de transport de mon établissement'
}

export const VenuePlaylist = ({
  onWholePlaylistSeen,
  trackPlaylistElementClicked,
}: VenuePlaylistProps) => {
  const { data: playlist, isLoading } = useSWR(
    [GET_LOCAL_OFFERERS_PLAYLIST_QUERY_KEY],
    () => apiAdage.getLocalOfferersPlaylist(),
    { fallbackData: { venues: [] } }
  )

  const distances = playlist.venues
    .map((venue) => venue.distance)
    .filter(Boolean) as number[]

  const distanceMax = distances.length === 0 ? 0 : Math.max(...distances)

  return (
    <Carousel
      title={
        <h2 className={styles['playlist-carousel-title']}>
          {getPlaylistTitle(distanceMax)}
        </h2>
      }
      className={classNames(styles['playlist-carousel'], {
        [styles['playlist-carousel-loading']]: isLoading,
      })}
      onLastCarouselElementVisible={() =>
        onWholePlaylistSeen({
          playlistId: VENUE_PLAYLIST,
          playlistType: AdagePlaylistType.VENUE,
        })
      }
      loading={isLoading}
      elements={playlist.venues.map((venue, index) => (
        <VenueCard
          key={venue.id}
          handlePlaylistElementTracking={() =>
            trackPlaylistElementClicked({
              playlistId: VENUE_PLAYLIST,
              playlistType: AdagePlaylistType.VENUE,
              index,
              elementId: venue.id,
            })
          }
          venue={venue}
        />
      ))}
    />
  )
}
