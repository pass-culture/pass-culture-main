import { createRef, useRef } from 'react'

import { AdagePlaylistType } from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useEducationalDomains } from '@/commons/hooks/swr/useEducationalDomains'
import { useIsElementVisible } from '@/commons/hooks/useIsElementVisible'
import { useNotification } from '@/commons/hooks/useNotification'

import styles from './AdageDiscovery.module.scss'
import { AdageDiscoveryBanner } from './AdageDiscoveryBanner/AdageDiscoveryBanner'
import { Carousel } from './Carousel/Carousel'
import { DOMAINS_PLAYLIST } from './constant'
import circles from './DomainsCard/assets/circles.svg'
import ellipses from './DomainsCard/assets/ellipses.svg'
import pills from './DomainsCard/assets/pills.svg'
import rectangles from './DomainsCard/assets/rectangles.svg'
import squares from './DomainsCard/assets/squares.svg'
import triangles from './DomainsCard/assets/triangles.svg'
import { DomainsCard } from './DomainsCard/DomainsCard'
import { ClassroomPlaylist } from './Playlist/ClassroomPlaylist/ClassroomPlaylist'
import { NewOffererPlaylist } from './Playlist/NewOffererPlaylist/NewOffererPlaylist'
import { NewOfferPlaylist } from './Playlist/NewOfferPlaylist/NewOfferPlaylist'
import { VenuePlaylist } from './Playlist/VenuePlaylist/VenuePlaylist'
import { PlaylistTracker } from './types'

export const AdageDiscovery = () => {
  const hasSeenAllPlaylist = useRef<boolean>(false)
  const params = new URLSearchParams(location.search)

  const footerSuggestion = createRef<HTMLDivElement>()
  const [isFooterSuggestionVisible] = useIsElementVisible(footerSuggestion)

  const notification = useNotification()
  const adageAuthToken = params.get('token')

  const discoveryRef = useRef<HTMLDivElement>(null)

  if (isFooterSuggestionVisible && !hasSeenAllPlaylist.current) {
    apiAdage.logHasSeenAllPlaylist({ iframeFrom: location.pathname })
    hasSeenAllPlaylist.current = true
  }

  const { data: educationalDomains, error: educationalDomainsApiError } =
    useEducationalDomains()

  if (educationalDomainsApiError) {
    notification.error(GET_DATA_ERROR_MESSAGE)
  }

  const domainsOptions = educationalDomains.map(({ id, name }) => ({
    value: id,
    label: name,
  }))

  function onWholePlaylistSeen({ playlistId, playlistType }: PlaylistTracker) {
    apiAdage.logHasSeenWholePlaylist({
      iframeFrom: location.pathname,
      playlistId,
      playlistType,
    })
  }

  const colorAndMotifOrder = [
    { color: 'orange', src: squares },
    { color: 'purple', src: pills },
    { color: 'pink', src: triangles },
    { color: 'green', src: rectangles },
    { color: 'red', src: ellipses },
    { color: 'blue', src: circles },
  ]

  const trackPlaylistElementClicked = (
    playlistTrackerParameters: PlaylistTracker
  ) => {
    apiAdage.logConsultPlaylistElement({
      iframeFrom: location.pathname,
      ...playlistTrackerParameters,
    })
  }

  return (
    <div className={styles['discovery']} ref={discoveryRef}>
      <AdageDiscoveryBanner />

      <div className={styles['discovery-playlists']}>
        <div className={styles['discovery-playlist']}>
          <NewOfferPlaylist
            onWholePlaylistSeen={onWholePlaylistSeen}
            trackPlaylistElementClicked={trackPlaylistElementClicked}
            observableRef={discoveryRef}
          />
        </div>
        <div className={styles['discovery-playlist']}>
          <Carousel
            title={
              <h2 className={styles['playlist-carousel-title']}>
                Explorez les domaines artistiques et culturels
              </h2>
            }
            observableRef={discoveryRef}
            onLastCarouselElementVisible={() =>
              onWholePlaylistSeen({
                playlistId: DOMAINS_PLAYLIST,
                playlistType: AdagePlaylistType.DOMAIN,
              })
            }
            elements={domainsOptions.map((elm, index) => {
              const colorAndMotif =
                colorAndMotifOrder[index % colorAndMotifOrder.length]

              return (
                <DomainsCard
                  handlePlaylistElementTracking={() =>
                    trackPlaylistElementClicked({
                      playlistId: DOMAINS_PLAYLIST,
                      playlistType: AdagePlaylistType.DOMAIN,
                      domainId: elm.value,
                      index,
                    })
                  }
                  key={`domains-${elm.value}`}
                  title={elm.label}
                  color={colorAndMotif.color}
                  src={colorAndMotif.src}
                  href={`/adage-iframe/recherche?token=${adageAuthToken}&domain=${elm.value}`}
                />
              )
            })}
          />
        </div>
        <div className={styles['discovery-playlist']}>
          <NewOffererPlaylist
            onWholePlaylistSeen={onWholePlaylistSeen}
            trackPlaylistElementClicked={trackPlaylistElementClicked}
            observableRef={discoveryRef}
          />
        </div>
        <div className={styles['discovery-playlist']}>
          <ClassroomPlaylist
            onWholePlaylistSeen={onWholePlaylistSeen}
            trackPlaylistElementClicked={trackPlaylistElementClicked}
            observableRef={discoveryRef}
          />
        </div>

        <div className={styles['discovery-playlist']} ref={footerSuggestion}>
          <VenuePlaylist
            onWholePlaylistSeen={onWholePlaylistSeen}
            trackPlaylistElementClicked={trackPlaylistElementClicked}
            observableRef={discoveryRef}
          />
        </div>
      </div>
    </div>
  )
}
