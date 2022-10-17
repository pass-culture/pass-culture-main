import React from 'react'

import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_STATUS_DRAFT } from 'core/Offers'
import { Offer } from 'core/Offers/types'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as PenIcon } from 'icons/ico-pen.svg'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

import styles from '../../OfferItem.module.scss'

const EditOfferCell = ({
  isOfferEditable,
  editionOfferLink,
  offer,
}: {
  isOfferEditable: boolean
  editionOfferLink: string
  offer: Offer
}) => {
  const { logEvent } = useAnalytics()
  return (
    <td className={styles['edit-column']}>
      {isOfferEditable && (
        <ButtonLink
          variant={ButtonVariant.SECONDARY}
          onClick={() =>
            logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
              from: OFFER_FORM_NAVIGATION_IN.OFFERS,
              to: OfferBreadcrumbStep.SUMMARY,
              used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_PEN,
              isEdition: true,
              isOfferDraft: offer.status === OFFER_STATUS_DRAFT,
              offerId: offer.id,
            })
          }
          link={{ isExternal: false, to: editionOfferLink }}
          className={styles['button']}
          Icon={PenIcon}
          iconPosition={IconPositionEnum.CENTER}
          hasTooltip
        >
          Modifier l’offre
        </ButtonLink>
      )}
    </td>
  )
}

export default EditOfferCell
