/* istanbul ignore file: DEBT, TO FIX */
import cn from 'classnames'
import React, { useEffect, useState } from 'react'

import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as ArrowIcon } from 'icons/ico-arrow-up-b.svg'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import { OFFER_WIZARD_STEP_IDS } from 'new_components/OfferIndividualStepper'
import { SummaryLayout } from 'new_components/SummaryLayout'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import type { IStockEventItemProps } from './StockEventItem'
import { StockEventItem } from './StockEventItem'
import styles from './StockEventSection.module.scss'

const NB_UNFOLDED_STOCK = 2

export interface IStockEventSectionProps {
  stocks: IStockEventItemProps[]
  offerId: string
}

const StockEventSection = ({
  stocks,
  offerId,
}: IStockEventSectionProps): JSX.Element => {
  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')
  const mode = useOfferWizardMode()
  const [showAllStocks, setShowAllStocks] = useState(false)
  const [displayedStocks, setDisplayedStocks] = useState(
    stocks.slice(0, NB_UNFOLDED_STOCK)
  )

  useEffect(() => {
    setDisplayedStocks(
      showAllStocks ? [...stocks] : stocks.slice(0, NB_UNFOLDED_STOCK)
    )
  }, [showAllStocks])

  const stocksUrlsV2 = {
    [OFFER_WIZARD_MODE.CREATION]: `/offre/${offerId}/individuel/creation/stocks`,
    [OFFER_WIZARD_MODE.DRAFT]: `/offre/${offerId}/individuel/brouillon/stocks`,
    [OFFER_WIZARD_MODE.EDITION]: `/offre/${offerId}/individuel/stocks`,
  }
  const editLink = isOfferFormV3
    ? getOfferIndividualUrl({
        offerId,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        mode,
      })
    : stocksUrlsV2[mode]
  const { logEvent } = useAnalytics()
  const logEditEvent = () => {
    /* istanbul ignore next: DEBT, TO FIX */
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OfferBreadcrumbStep.SUMMARY,
      to: OfferBreadcrumbStep.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.RECAP_LINK,
      isEdition: mode === OFFER_WIZARD_MODE.EDITION,
      isDraft: mode === OFFER_WIZARD_MODE.DRAFT,
      offerId: offerId,
    })
  }
  return (
    <SummaryLayout.Section
      title="Stocks et prix"
      editLink={editLink}
      onLinkClick={logEditEvent}
    >
      {displayedStocks.map((s, k) => (
        <StockEventItem
          key={`stock-${k}`}
          className={styles['stock-event-item']}
          beginningDatetime={s.beginningDatetime}
          price={s.price}
          quantity={s.quantity}
          bookingLimitDatetime={s.bookingLimitDatetime}
          departmentCode={s.departmentCode}
        />
      ))}

      {stocks.length > NB_UNFOLDED_STOCK && (
        <Button
          className={styles['stock-event-item-display-more']}
          Icon={() => (
            <ArrowIcon
              className={
                /* istanbul ignore next: DEBT, TO FIX */
                cn(styles['stock-event-item-display-more-icon'], {
                  [styles['stock-event-item-display-more-icon-down']]:
                    !showAllStocks,
                })
              }
            />
          )}
          variant={ButtonVariant.TERNARY}
          onClick={() => setShowAllStocks(!showAllStocks)}
        >
          {showAllStocks ? 'Afficher moins de dates' : 'Afficher plus de dates'}
        </Button>
      )}
    </SummaryLayout.Section>
  )
}

export default StockEventSection
