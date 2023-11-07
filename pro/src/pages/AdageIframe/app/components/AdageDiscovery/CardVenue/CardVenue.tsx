import React from 'react'
import { useNavigate } from 'react-router-dom'

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
}

const CardVenue = ({ venue }: CardVenueProps) => {
  const params = new URLSearchParams(location.search)
  const adageAuthToken = params.get('token')
  const navigate = useNavigate()
  return (
    <button
      className={styles.container}
      onClick={() =>
        navigate(`/adage-iframe/venue/${venue.id}?token=${adageAuthToken}`)
      }
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
    </button>
  )
}

export default CardVenue
