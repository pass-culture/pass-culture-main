import { useEffect, useState } from 'react'

import { CollectiveOfferTemplateResponseModel } from 'apiClient/adage'
import { AdagePlaylistType } from 'apiClient/adage/models/AdagePlaylistType'
import { apiAdage } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import useNotification from 'hooks/useNotification'

import { TrackerElementArg } from '../AdageDiscovery'
import styles from '../AdageDiscovery.module.scss'
import Carousel from '../Carousel/Carousel'
import { NEW_OFFER_PLAYLIST } from '../constant'
import OfferCardComponent from '../OfferCard/OfferCard'

type NewOfferPlaylistProps = {
  onWholePlaylistSeen: ({ playlistId, playlistType }: TrackerElementArg) => void
  trackPlaylistElementClicked: ({
    playlistId,
    playlistType,
    elementId,
  }: TrackerElementArg) => void
}

export const NewOfferPlaylist = ({
  onWholePlaylistSeen,
  trackPlaylistElementClicked,
}: NewOfferPlaylistProps) => {
  const [offers, setOffers] = useState<CollectiveOfferTemplateResponseModel[]>(
    []
  )
  const notify = useNotification()

  useEffect(() => {
    const getNewOfferPlaylist = async () => {
      try {
        const result = await apiAdage.newTemplateOffersPlaylist()

        setOffers(result.collectiveOffers)
      } catch (e) {
        return notify.error(GET_DATA_ERROR_MESSAGE)
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    getNewOfferPlaylist()
  }, [notify])

  return (
    <Carousel
      title={
        <h2 className={styles['section-title']}>
          Les offres publiées récemment
        </h2>
      }
      onLastCarouselElementVisible={() =>
        onWholePlaylistSeen({
          playlistId: NEW_OFFER_PLAYLIST,
          playlistType: AdagePlaylistType.OFFER,
        })
      }
      elements={offers.map((offerElement, elementId) => (
        <OfferCardComponent
          handlePlaylistElementTracking={() =>
            trackPlaylistElementClicked({
              playlistId: NEW_OFFER_PLAYLIST,
              playlistType: AdagePlaylistType.OFFER,
              elementId,
            })
          }
          key={`card-offer-${elementId}`}
          offer={offerElement}
        />
      ))}
    />
  )
}
