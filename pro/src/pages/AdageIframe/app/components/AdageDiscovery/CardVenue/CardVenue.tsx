import React from 'react'
import { useSearchParams } from 'react-router-dom'

import styles from './CardVenue.module.scss'

interface CardVenueModel {
  imageUrl: string
  name: string
  publicName?: string
  distance: number
  id: string
  city: string
}

export interface CardVenueProps {
  venue: CardVenueModel
  handlePlaylistElementTracking: () => void
}

const CardVenue = ({
  venue,
  handlePlaylistElementTracking,
}: CardVenueProps) => {
  const [searchParams] = useSearchParams()
  const adageAuthToken = searchParams.get('token')

  return (
    <a
      data-testid="card-venue-link"
      className={styles.container}
      href={`/adage-iframe/venue/${venue.id}?token=${adageAuthToken}`}
      onClick={() => handlePlaylistElementTracking()}
    >
      <img
        alt=""
        className={styles['venue-image']}
        loading="lazy"
        src={venue.imageUrl}
      />
      <div className={styles['venue-infos']}>
        <div className={styles['venue-infos-name']}>
          {venue.publicName || venue.name}
        </div>
        <div
          className={styles['venue-infos-distance']}
        >{`à ${venue.distance} km - ${venue.city}`}</div>
      </div>
    </a>
  )
}

export default CardVenue
