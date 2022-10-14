import React from 'react'

import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as GuichetFullIcon } from 'icons/ico-guichet-full.svg'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from '../../OfferItem.module.scss'

const EditStocksCell = ({ editionStockLink }: { editionStockLink: string }) => {
  const { logEvent } = useAnalytics()

  return (
    <td className={styles['switch-column']}>
      <ButtonLink
        variant={ButtonVariant.SECONDARY}
        onClick={() =>
          logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
            from: OFFER_FORM_NAVIGATION_IN.OFFERS,
            to: OfferBreadcrumbStep.STOCKS,
            used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_STOCKS,
            isEdition: true,
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
