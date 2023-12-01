import React from 'react'
import { NavLink, useSearchParams } from 'react-router-dom'

import strokeVenueIcon from 'icons/stroke-venue.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './CardVenue.module.scss'

interface CardVenueModel {
  imageUrl?: string | null
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
    <NavLink
      data-testid="card-venue-link"
      className={styles.container}
      to={`/adage-iframe/recherche?token=${adageAuthToken}&venue=${venue.id}`}
      onClick={() => handlePlaylistElementTracking()}
    >
      {venue.imageUrl ? (
        <img
          alt=""
          className={styles['venue-image']}
          loading="lazy"
          src={venue.imageUrl}
        />
      ) : (
        <div
          className={`${styles['venue-image']} ${styles['venue-image-fallback']}`}
        >
          <SvgIcon src={strokeVenueIcon} width="80" alt="" />
        </div>
      )}
      <div className={styles['venue-infos']}>
        <div className={styles['venue-infos-name']}>
          {venue.publicName || venue.name}
        </div>
        <div
          className={styles['venue-infos-distance']}
        >{`à ${venue.distance} km - ${venue.city}`}</div>
      </div>
    </NavLink>
  )
}

export default CardVenue
