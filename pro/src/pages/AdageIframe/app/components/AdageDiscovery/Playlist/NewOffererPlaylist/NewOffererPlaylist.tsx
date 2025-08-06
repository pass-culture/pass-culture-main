import classNames from 'classnames'
import useSWR from 'swr'

import { AdagePlaylistType } from '@/apiClient/adage/models/AdagePlaylistType'
import { apiAdage } from '@/apiClient/api'
import { GET_NEW_OFFERERS_PLAYLIST_QUERY_KEY } from '@/commons/config/swrQueryKeys'

import { Carousel } from '../../Carousel/Carousel'
import { NEW_VENUE_PLAYLIST } from '../../constant'
import { PlaylistTracker, VenuePlaylistTracker } from '../../types'
import { VenueCard } from '../../VenueCard/VenueCard'
import styles from './NewOffererPlaylist.module.scss'

type NewOffererPlaylistProps = {
  onWholePlaylistSeen: ({ playlistId, playlistType }: PlaylistTracker) => void
  trackPlaylistElementClicked: ({
    playlistId,
    playlistType,
    venueId,
    index,
  }: VenuePlaylistTracker) => void
  observableRef?: React.RefObject<HTMLDivElement>
}

export const NewOffererPlaylist = ({
  onWholePlaylistSeen,
  trackPlaylistElementClicked,
  observableRef,
}: NewOffererPlaylistProps) => {
  const { data: playlist, isLoading } = useSWR(
    [GET_NEW_OFFERERS_PLAYLIST_QUERY_KEY],
    () => apiAdage.getNewOfferersPlaylist(),
    { fallbackData: { venues: [] } }
  )

  return (
    <Carousel
      title={
        <h2 className={styles['playlist-carousel-title']}>
          Ces partenaires culturels ont été récemment référencés
        </h2>
      }
      className={classNames(styles['playlist-carousel'], {
        [styles['playlist-carousel-loading']]: isLoading,
      })}
      observableRef={observableRef}
      onLastCarouselElementVisible={() =>
        onWholePlaylistSeen({
          playlistId: NEW_VENUE_PLAYLIST,
          playlistType: AdagePlaylistType.VENUE,
        })
      }
      loading={isLoading}
      elements={playlist.venues.map((venue, index) => (
        <VenueCard
          key={venue.id}
          handlePlaylistElementTracking={() =>
            trackPlaylistElementClicked({
              playlistId: NEW_VENUE_PLAYLIST,
              playlistType: AdagePlaylistType.VENUE,
              index,
              venueId: venue.id,
            })
          }
          venue={venue}
        />
      ))}
    />
  )
}
