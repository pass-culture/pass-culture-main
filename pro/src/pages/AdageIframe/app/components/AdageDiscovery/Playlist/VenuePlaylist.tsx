import { useEffect, useState } from 'react'

import { LocalOfferersPlaylistOffer } from 'apiClient/adage'
import { AdagePlaylistType } from 'apiClient/adage/models/AdagePlaylistType'
import { apiAdage } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import useNotification from 'hooks/useNotification'

import { TrackerElementArg } from '../AdageDiscovery'
import styles from '../AdageDiscovery.module.scss'
import Carousel from '../Carousel/Carousel'
import { VENUE_PLAYLIST } from '../constant'
import VenueCard from '../VenueCard/VenueCard'

type VenuePlaylistProps = {
  onWholePlaylistSeen: ({ playlistId, playlistType }: TrackerElementArg) => void
  trackPlaylistElementClicked: ({
    playlistId,
    playlistType,
    elementId,
  }: TrackerElementArg) => void
}

export const VenuePlaylist = ({
  onWholePlaylistSeen,
  trackPlaylistElementClicked,
}: VenuePlaylistProps) => {
  const [venues, setVenues] = useState<LocalOfferersPlaylistOffer[]>([])
  const notify = useNotification()

  useEffect(() => {
    const getClassroomPlaylistOffer = async () => {
      try {
        const result = await apiAdage.getLocalOfferersPlaylist()

        setVenues(result.venues)
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
          À moins de 30 minutes à pied de votre établissement
        </h2>
      }
      onLastCarouselElementVisible={() =>
        onWholePlaylistSeen({
          playlistId: VENUE_PLAYLIST,
          playlistType: AdagePlaylistType.VENUE,
        })
      }
      elements={venues.map((venue, index) => (
        <VenueCard
          key={`card-venue-${index}`}
          handlePlaylistElementTracking={() =>
            trackPlaylistElementClicked({
              playlistId: VENUE_PLAYLIST,
              playlistType: AdagePlaylistType.VENUE,
              elementId: index,
            })
          }
          venue={venue}
        />
      ))}
    ></Carousel>
  )
}
