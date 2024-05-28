import classNames from 'classnames'
import { useEffect, useState } from 'react'

import { CollectiveOfferTemplateResponseModel } from 'apiClient/adage'
import { AdagePlaylistType } from 'apiClient/adage/models/AdagePlaylistType'
import { apiAdage } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import useNotification from 'hooks/useNotification'

import { TrackerElementArg } from '../../AdageDiscovery'
import { Carousel } from '../../Carousel/Carousel'
import { NEW_OFFER_PLAYLIST } from '../../constant'
import OfferCardComponent from '../../OfferCard/OfferCard'

import styles from './NewOfferPlaylist.module.scss'

type NewOfferPlaylistProps = {
  onWholePlaylistSeen: ({ playlistId, playlistType }: TrackerElementArg) => void
  trackPlaylistElementClicked: ({
    playlistId,
    playlistType,
    elementId,
    index,
  }: TrackerElementArg) => void
}

export const NewOfferPlaylist = ({
  onWholePlaylistSeen,
  trackPlaylistElementClicked,
}: NewOfferPlaylistProps) => {
  const [offers, setOffers] = useState<CollectiveOfferTemplateResponseModel[]>(
    []
  )
  const [loading, setLoading] = useState<boolean>(false)
  const { error } = useNotification()

  useEffect(() => {
    const getNewOfferPlaylist = async () => {
      setLoading(true)
      try {
        const result = await apiAdage.newTemplateOffersPlaylist()

        setOffers(result.collectiveOffers)
      } catch (e) {
        return error(GET_DATA_ERROR_MESSAGE)
      } finally {
        setLoading(false)
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    getNewOfferPlaylist()
  }, [error])

  return (
    <Carousel
      title={
        <h2 className={styles['playlist-carousel-title']}>
          Les offres publiées récemment
        </h2>
      }
      className={classNames(styles['playlist-carousel'], {
        [styles['playlist-carousel-loading']]: loading,
      })}
      loading={loading}
      onLastCarouselElementVisible={() =>
        onWholePlaylistSeen({
          playlistId: NEW_OFFER_PLAYLIST,
          playlistType: AdagePlaylistType.OFFER,
        })
      }
      elements={offers.map((offer, index) => (
        <OfferCardComponent
          onCardClicked={() =>
            trackPlaylistElementClicked({
              playlistId: NEW_OFFER_PLAYLIST,
              playlistType: AdagePlaylistType.OFFER,
              index,
              elementId: offer.id,
            })
          }
          key={offer.id}
          offer={offer}
        />
      ))}
    />
  )
}
