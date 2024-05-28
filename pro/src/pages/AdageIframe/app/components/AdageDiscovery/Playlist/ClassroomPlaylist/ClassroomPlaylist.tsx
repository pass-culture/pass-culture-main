import classNames from 'classnames'
import useSWR from 'swr'

import { AdagePlaylistType } from 'apiClient/adage/models/AdagePlaylistType'
import { apiAdage } from 'apiClient/api'
import { GET_CLASSROOM_PLAYLIST_QUERY_KEY } from 'config/swrQueryKeys'

import { TrackerElementArg } from '../../AdageDiscovery'
import { Carousel } from '../../Carousel/Carousel'
import { CLASSROOM_PLAYLIST } from '../../constant'
import OfferCardComponent from '../../OfferCard/OfferCard'

import styles from './ClassroomPlaylist.module.scss'

type ClassroomPlaylistProps = {
  onWholePlaylistSeen: ({ playlistId, playlistType }: TrackerElementArg) => void
  trackPlaylistElementClicked: ({
    playlistId,
    playlistType,
    elementId,
    index,
  }: TrackerElementArg) => void
}

export const ClassroomPlaylist = ({
  onWholePlaylistSeen,
  trackPlaylistElementClicked,
}: ClassroomPlaylistProps) => {
  const { data: classRoomPlaylist, isLoading } = useSWR(
    [GET_CLASSROOM_PLAYLIST_QUERY_KEY],
    () => apiAdage.getClassroomPlaylist(),
    { fallbackData: { collectiveOffers: [] } }
  )

  return (
    <Carousel
      className={classNames(styles['playlist-carousel'], {
        [styles['playlist-carousel-loading']]: isLoading,
      })}
      title={
        <h2 className={styles['playlist-carousel-title']}>
          Ces interventions peuvent avoir lieu dans votre établissement
        </h2>
      }
      onLastCarouselElementVisible={() =>
        onWholePlaylistSeen({
          playlistId: CLASSROOM_PLAYLIST,
          playlistType: AdagePlaylistType.OFFER,
        })
      }
      loading={isLoading}
      elements={classRoomPlaylist.collectiveOffers.map(
        (offerElement, index) => (
          <OfferCardComponent
            onCardClicked={() =>
              trackPlaylistElementClicked({
                playlistId: CLASSROOM_PLAYLIST,
                playlistType: AdagePlaylistType.OFFER,
                index,
                elementId: offerElement.id,
              })
            }
            key={`card-offer-class-${offerElement.id}`}
            offer={offerElement}
          />
        )
      )}
    />
  )
}
