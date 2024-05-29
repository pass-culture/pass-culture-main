import { Link, useSearchParams } from 'react-router-dom'

import { LocalOfferersPlaylistOffer } from 'apiClient/adage'
import strokeInstitutionIcon from 'icons/stroke-institution.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './VenueCard.module.scss'

export interface VenueCardProps {
  venue: LocalOfferersPlaylistOffer
  handlePlaylistElementTracking: () => void
}

export const VenueCard = ({
  venue,
  handlePlaylistElementTracking,
}: VenueCardProps) => {
  const [searchParams] = useSearchParams()
  const adageAuthToken = searchParams.get('token')

  return (
    <Link
      data-testid="card-venue-link"
      className={styles.container}
      to={`/adage-iframe/recherche?token=${adageAuthToken}&venue=${venue.id}`}
      onClick={() => handlePlaylistElementTracking()}
    >
      {venue.imgUrl ? (
        <img
          alt=""
          className={styles['venue-image']}
          loading="lazy"
          src={venue.imgUrl}
        />
      ) : (
        <div
          className={`${styles['venue-image']} ${styles['venue-image-fallback']}`}
        >
          <SvgIcon src={strokeInstitutionIcon} width="80" alt="" />
        </div>
      )}
      <div className={styles['venue-infos']}>
        <div
          data-testid="venue-infos-name"
          className={styles['venue-infos-name']}
        >
          {venue.publicName || venue.name}
        </div>
        <div
          className={styles['venue-infos-distance']}
        >{`à ${venue.distance} km - ${venue.city}`}</div>
      </div>
    </Link>
  )
}
