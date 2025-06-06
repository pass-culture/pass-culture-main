import classNames from 'classnames'
import useSWR from 'swr'

import { AdagePlaylistType } from 'apiClient/adage/models/AdagePlaylistType'
import { apiAdage } from 'apiClient/api'
import { GET_CLASSROOM_PLAYLIST_QUERY_KEY } from 'commons/config/swrQueryKeys'

import { Carousel } from '../../Carousel/Carousel'
import { CLASSROOM_PLAYLIST } from '../../constant'
import { OfferCardComponent } from '../../OfferCard/OfferCard'
import { OfferPlaylistTracker, PlaylistTracker } from '../../types'

import styles from './ClassroomPlaylist.module.scss'

type ClassroomPlaylistProps = {
  onWholePlaylistSeen: ({ playlistId, playlistType }: PlaylistTracker) => void
  trackPlaylistElementClicked: ({
    playlistId,
    playlistType,
    offerId,
    index,
  }: OfferPlaylistTracker) => void
  observableRef?: React.RefObject<HTMLDivElement>
}

export const ClassroomPlaylist = ({
  onWholePlaylistSeen,
  trackPlaylistElementClicked,
  observableRef,
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
      observableRef={observableRef}
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
                offerId: offerElement.id,
              })
            }
            key={`card-offer-class-${offerElement.id}`}
            offer={offerElement}
            playlistId={CLASSROOM_PLAYLIST}
          />
        )
      )}
    />
  )
}
