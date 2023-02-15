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
import { PenIcon } from 'icons'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

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
      offerId: offer.id,
    })
  }

  return (
    <td className={styles['edit-column']}>
      <ButtonLink
        variant={ButtonVariant.SECONDARY}
        onClick={onEditOfferClick}
        link={{ isExternal: false, to: editionOfferLink }}
        className={styles['button']}
        Icon={PenIcon}
        iconPosition={IconPositionEnum.CENTER}
        hasTooltip
      >
        Modifier l’offre
      </ButtonLink>
    </td>
  )
}

export default EditOfferCell
