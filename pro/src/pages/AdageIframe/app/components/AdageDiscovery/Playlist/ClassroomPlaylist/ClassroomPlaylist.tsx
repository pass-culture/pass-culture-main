import classNames from 'classnames'
import { useEffect, useState } from 'react'

import { CollectiveOfferTemplateResponseModel } from 'apiClient/adage'
import { AdagePlaylistType } from 'apiClient/adage/models/AdagePlaylistType'
import { apiAdage } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import useNotification from 'hooks/useNotification'

import { TrackerElementArg } from '../../AdageDiscovery'
import Carousel from '../../Carousel/Carousel'
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
  const [offers, setOffers] = useState<CollectiveOfferTemplateResponseModel[]>(
    []
  )
  const [loading, setLoading] = useState<boolean>(false)
  const { error } = useNotification()

  useEffect(() => {
    const getClassroomPlaylistOffer = async () => {
      setLoading(true)
      try {
        const result = await apiAdage.getClassroomPlaylist()

        setOffers(result.collectiveOffers)
      } catch (e) {
        error(GET_DATA_ERROR_MESSAGE)
      } finally {
        setLoading(false)
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    getClassroomPlaylistOffer()
  }, [error])

  return (
    <Carousel
      className={classNames(styles['playlist-carousel'], {
        [styles['playlist-carousel-loading']]: loading,
      })}
      title={
        <h2 className={styles['playlist-carousel-title']}>
          Ces interventions peuvent avoir lieu dans votre classe
        </h2>
      }
      onLastCarouselElementVisible={() =>
        onWholePlaylistSeen({
          playlistId: CLASSROOM_PLAYLIST,
          playlistType: AdagePlaylistType.OFFER,
        })
      }
      loading={loading}
      elements={offers.map((offerElement, index) => (
        <OfferCardComponent
          handlePlaylistElementTracking={() =>
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
      ))}
    />
  )
}
