import { useEffect, useState } from 'react'

import {
  InstitutionRuralLevel,
  LocalOfferersPlaylistOffer,
} from 'apiClient/adage'
import { AdagePlaylistType } from 'apiClient/adage/models/AdagePlaylistType'
import { apiAdage } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import useNotification from 'hooks/useNotification'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'

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

const institutionRuralLevelToPlaylistTitle: {
  [key in InstitutionRuralLevel]: string
} = {
  'urbain dense': 'À moins 30 minutes à pieds de mon établissement',
  'urbain densité intermédiaire':
    'À moins de 30 minutes en transport de mon établissement',
  "rural sous forte influence d'un pôle":
    'À environ de 30 minutes de transport de mon établissement',
  'rural autonome peu dense': 'À environs 1h de transport de mon établissement',
  "rural sous faible influence d'un pôle":
    'À environs 1h de transport de mon établissement',
  'rural autonome très peu dense':
    'À environs 1h de transport de mon établissement',
}

export const VenuePlaylist = ({
  onWholePlaylistSeen,
  trackPlaylistElementClicked,
}: VenuePlaylistProps) => {
  const [venues, setVenues] = useState<LocalOfferersPlaylistOffer[]>([])
  const notify = useNotification()
  const { adageUser } = useAdageUser()

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
          {adageUser.institutionRuralLevel
            ? institutionRuralLevelToPlaylistTitle[
                adageUser.institutionRuralLevel
              ]
            : 'À moins 30 minutes à pieds de mon établissement'}
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
