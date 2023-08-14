import React from 'react'
import { Link } from 'react-router-dom'

import { Offer } from 'core/Offers/types'
import Thumb from 'ui-kit/Thumb'

import styles from '../../OfferItem.module.scss'

const ThumbCell = ({
  offer,
  editionOfferLink,
  onThumbClick,
}: {
  offer: Offer
  editionOfferLink: string
  onThumbClick?: () => void
}) => {
  return (
    <td className={styles['thumb-column']}>
      <Link
        className={styles['name']}
        title={`${offer.name} - éditer l’offre`}
        onClick={onThumbClick}
        to={editionOfferLink}
      >
        <Thumb url={offer.thumbUrl} className={styles['offer-thumb']} />
      </Link>
    </td>
  )
}

export default ThumbCell
