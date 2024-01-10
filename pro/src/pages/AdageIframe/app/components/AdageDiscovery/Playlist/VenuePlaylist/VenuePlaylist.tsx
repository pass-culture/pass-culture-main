import classNames from 'classnames'
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

import { TrackerElementArg } from '../../AdageDiscovery'
import Carousel from '../../Carousel/Carousel'
import { VENUE_PLAYLIST } from '../../constant'
import VenueCard from '../../VenueCard/VenueCard'

import styles from './VenuePlaylist.module.scss'

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
  'urbain dense': 'À moins de 30 minutes à pied de mon établissement',
  'urbain densité intermédiaire':
    'À moins de 30 minutes de route de mon établissement',
  "rural sous forte influence d'un pôle":
    'À environ 30 minutes de route de mon établissement',
  'rural autonome peu dense': 'À environ 1h de route de mon établissement',
  "rural sous faible influence d'un pôle":
    'À environ 1h de route de mon établissement',
  'rural autonome très peu dense': 'À environ 1h de route de mon établissement',
}

export const VenuePlaylist = ({
  onWholePlaylistSeen,
  trackPlaylistElementClicked,
}: VenuePlaylistProps) => {
  const [venues, setVenues] = useState<LocalOfferersPlaylistOffer[]>([])

  const { adageUser } = useAdageUser()
  const [loading, setLoading] = useState<boolean>(false)
  const { error } = useNotification()

  useEffect(() => {
    const getClassroomPlaylistOffer = async () => {
      setLoading(true)
      try {
        const result = await apiAdage.getLocalOfferersPlaylist()
        setVenues(result.venues)
      } catch (e) {
        return error(GET_DATA_ERROR_MESSAGE)
      } finally {
        setLoading(false)
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    getClassroomPlaylistOffer()
  }, [error])

  return (
    <Carousel
      title={
        <h2 className={styles['playlist-carousel-title']}>
          {adageUser.institutionRuralLevel
            ? institutionRuralLevelToPlaylistTitle[
                adageUser.institutionRuralLevel
              ]
            : 'À moins de 30 minutes à pied de mon établissement'}
        </h2>
      }
      className={classNames(styles['playlist-carousel'], {
        [styles['playlist-carousel-loading']]: loading,
      })}
      onLastCarouselElementVisible={() =>
        onWholePlaylistSeen({
          playlistId: VENUE_PLAYLIST,
          playlistType: AdagePlaylistType.VENUE,
        })
      }
      loading={loading}
      elements={venues.map((venue, index) => (
        <VenueCard
          key={venue.id}
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
