import React from 'react'
import { Link } from 'react-router-dom'

import { OfferBreadcrumbStep } from 'components/OfferBreadcrumb'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_STATUS_DRAFT } from 'core/Offers'
import { Offer } from 'core/Offers/types'
import useAnalytics from 'hooks/useAnalytics'
import Thumb from 'ui-kit/Thumb'

import styles from '../../OfferItem.module.scss'

const ThumbCell = ({
  offer,
  editionOfferLink,
}: {
  offer: Offer
  editionOfferLink: string
}) => {
  const { logEvent } = useAnalytics()

  const onThumbClick = () => {
    const isDraft = offer.status === OFFER_STATUS_DRAFT
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_FORM_NAVIGATION_IN.OFFERS,
      to: isDraft ? OfferBreadcrumbStep.DETAILS : OfferBreadcrumbStep.SUMMARY,
      used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_THUMB,
      isEdition: true,
      isDraft: isDraft,
      offerId: offer.id,
    })
  }

  return (
    <td className={styles['thumb-column']}>
      <Link
        className={styles['name']}
        title={`${offer.name} - éditer l’offre`}
        onClick={onThumbClick}
        to={editionOfferLink}
      >
        <Thumb
          alt={`${offer.name} - éditer l’offre`}
          url={offer.thumbUrl}
          className={styles['offer-thumb']}
        />
      </Link>
    </td>
  )
}

export default ThumbCell
