import classNames from 'classnames'
import useSWR from 'swr'

import { AdagePlaylistType } from '@/apiClient/adage/models/AdagePlaylistType'
import { apiAdage } from '@/apiClient/api'
import { GET_NEW_OFFERS_PLAYLIST_KEY } from '@/commons/config/swrQueryKeys'

import { Carousel } from '../../Carousel/Carousel'
import { NEW_OFFER_PLAYLIST } from '../../constant'
import { OfferCardComponent } from '../../OfferCard/OfferCard'
import type { OfferPlaylistTracker, PlaylistTracker } from '../../types'
import styles from './NewOfferPlaylist.module.scss'

type NewOfferPlaylistProps = {
  onWholePlaylistSeen: ({
    playlistId,
    playlistType,
    numberOfTiles,
  }: PlaylistTracker) => void
  trackPlaylistElementClicked: ({
    playlistId,
    playlistType,
    offerId,
    index,
  }: OfferPlaylistTracker) => void
  observableRef?: React.RefObject<HTMLDivElement>
}

export const NewOfferPlaylist = ({
  onWholePlaylistSeen,
  trackPlaylistElementClicked,
  observableRef,
}: NewOfferPlaylistProps) => {
  const { data: playlist, isLoading } = useSWR(
    [GET_NEW_OFFERS_PLAYLIST_KEY],
    () => apiAdage.newTemplateOffersPlaylist(),
    { fallbackData: { collectiveOffers: [] } }
  )

  return (
    <Carousel
      title={
        <h2 className={styles['playlist-carousel-title']}>
          Les offres publiées récemment
        </h2>
      }
      className={classNames(styles['playlist-carousel'], {
        [styles['playlist-carousel-loading']]: isLoading,
      })}
      observableRef={observableRef}
      loading={isLoading}
      onLastCarouselElementVisible={() =>
        onWholePlaylistSeen({
          playlistId: NEW_OFFER_PLAYLIST,
          playlistType: AdagePlaylistType.OFFER,
          numberOfTiles: playlist.collectiveOffers.length,
        })
      }
      elements={playlist.collectiveOffers.map((offer, index) => (
        <OfferCardComponent
          onCardClicked={() =>
            trackPlaylistElementClicked({
              playlistId: NEW_OFFER_PLAYLIST,
              playlistType: AdagePlaylistType.OFFER,
              index,
              offerId: offer.id,
            })
          }
          key={offer.id}
          offer={offer}
          playlistId={NEW_OFFER_PLAYLIST}
        />
      ))}
    />
  )
}
