import React from 'react'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_STATUS_DRAFT } from 'core/Offers'
import { Offer } from 'core/Offers/types'
import useAnalytics from 'hooks/useAnalytics'
import penIcon from 'icons/full-edit.svg'
import ListIconButton from 'ui-kit/ListIconButton/ListIconButton'

import styles from '../../OfferItem.module.scss'

const EditOfferCell = ({
  editionOfferLink,
  offer,
}: {
  isOfferEditable: boolean
  editionOfferLink: string
  offer: Offer
}) => {
  const { logEvent } = useAnalytics()

  const onEditOfferClick = () => {
    const isDraft = offer.status === OFFER_STATUS_DRAFT

    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_FORM_NAVIGATION_IN.OFFERS,
      to: !isDraft
        ? OFFER_WIZARD_STEP_IDS.SUMMARY
        : OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_PEN,
      isEdition: true,
      isDraft: isDraft,
      offerId: offer.nonHumanizedId,
    })
  }

  return (
    <ListIconButton
      onClick={onEditOfferClick}
      url={editionOfferLink}
      className={styles['button']}
      icon={penIcon}
      hasTooltip
    >
      Modifier
    </ListIconButton>
  )
}

export default EditOfferCell
