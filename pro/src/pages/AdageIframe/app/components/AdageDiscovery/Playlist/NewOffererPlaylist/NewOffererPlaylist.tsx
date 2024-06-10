import classNames from 'classnames'
import useSWR from 'swr'

import { AdagePlaylistType } from 'apiClient/adage/models/AdagePlaylistType'
import { apiAdage } from 'apiClient/api'
import { GET_NEW_OFFERERS_PLAYLIST_QUERY_KEY } from 'config/swrQueryKeys'

import { TrackerElementArg } from '../../AdageDiscovery'
import { Carousel } from '../../Carousel/Carousel'
import { VENUE_PLAYLIST } from '../../constant'
import { VenueCard } from '../../VenueCard/VenueCard'

import styles from './NewOffererPlaylist.module.scss'

type NewOffererPlaylistProps = {
  onWholePlaylistSeen: ({ playlistId, playlistType }: TrackerElementArg) => void
  trackPlaylistElementClicked: ({
    playlistId,
    playlistType,
    elementId,
    index,
  }: TrackerElementArg) => void
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
