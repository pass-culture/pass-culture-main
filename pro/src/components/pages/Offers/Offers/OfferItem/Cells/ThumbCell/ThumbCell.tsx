import React from 'react'
import { Link } from 'react-router-dom'

import useAnalytics from 'components/hooks/useAnalytics'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { Offer } from 'core/Offers/types'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
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
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_FORM_NAVIGATION_IN.OFFERS,
      to: OfferBreadcrumbStep.SUMMARY,
      used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_THUMB,
      isEdition: true,
    })
  }

  return (
    <td className="thumb-column">
      <Link
        className="name"
        title={`${offer.name} - éditer l'offre`}
        onClick={onThumbClick}
        to={editionOfferLink}
      >
        <Thumb
          alt={`${offer.name} - éditer l'offre`}
          url={offer.thumbUrl}
          className={styles['offer-thumb']}
        />
      </Link>
    </td>
  )
}

export default ThumbCell
