import React from 'react'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { Offer } from 'core/Offers/types'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as GuichetFullIcon } from 'icons/ico-guichet-full.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from '../../OfferItem.module.scss'

const EditStocksCell = ({
  editionStockLink,
  offer,
}: {
  editionStockLink: string
  offer: Offer
}) => {
  const { logEvent } = useAnalytics()

  return (
    <td className={styles['switch-column']}>
      <ButtonLink
        variant={ButtonVariant.SECONDARY}
        onClick={() =>
          logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
            from: OFFER_FORM_NAVIGATION_IN.OFFERS,
            to: OFFER_WIZARD_STEP_IDS.STOCKS,
            used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_STOCKS,
            isEdition: true,
            offerId: offer.id,
            isDraft: false,
          })
        }
        link={{ isExternal: false, to: editionStockLink }}
        Icon={GuichetFullIcon}
      >
        Stocks
      </ButtonLink>
    </td>
  )
}

export default EditStocksCell
