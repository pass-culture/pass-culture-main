import { useEffect, useState } from 'react'

import { CollectiveOfferTemplateResponseModel } from 'apiClient/adage'
import { AdagePlaylistType } from 'apiClient/adage/models/AdagePlaylistType'
import { apiAdage } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import useNotification from 'hooks/useNotification'

import { TrackerElementArg } from '../AdageDiscovery'
import styles from '../AdageDiscovery.module.scss'
import Carousel from '../Carousel/Carousel'
import { CLASSROOM_PLAYLIST } from '../constant'
import OfferCardComponent from '../OfferCard/OfferCard'

type ClassroomPlaylistProps = {
  onWholePlaylistSeen: ({ playlistId, playlistType }: TrackerElementArg) => void
  trackPlaylistElementClicked: ({
    playlistId,
    playlistType,
    elementId,
  }: TrackerElementArg) => void
}

export const ClassroomPlaylist = ({
  onWholePlaylistSeen,
  trackPlaylistElementClicked,
}: ClassroomPlaylistProps) => {
  const [offers, setOffers] = useState<CollectiveOfferTemplateResponseModel[]>(
    []
  )
  const notify = useNotification()

  useEffect(() => {
    const getClassroomPlaylistOffer = async () => {
      try {
        const result = await apiAdage.getClassroomPlaylist()

        setOffers(result.collectiveOffers)
      } catch (e) {
        return notify.error(GET_DATA_ERROR_MESSAGE)
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    getClassroomPlaylistOffer()
  }, [notify])

  return (
    <Carousel
      title={
        <h2 className={styles['section-title']}>
          Ces interventions peuvent avoir lieu dans votre classe
        </h2>
      }
      onLastCarouselElementVisible={() =>
        onWholePlaylistSeen({
          playlistId: CLASSROOM_PLAYLIST,
          playlistType: AdagePlaylistType.OFFER,
        })
      }
      elements={offers.map((offerElement, index) => (
        <OfferCardComponent
          handlePlaylistElementTracking={() =>
            trackPlaylistElementClicked({
              playlistId: CLASSROOM_PLAYLIST,
              playlistType: AdagePlaylistType.OFFER,
              elementId: index,
            })
          }
          key={`card-offer-class-${offerElement.id}`}
          offer={offerElement}
        />
      ))}
    />
  )
}
