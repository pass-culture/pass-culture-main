import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { SummaryLayout } from 'components/SummaryLayout'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'

import { IStockEventItemProps, StockEventSection } from './StockEventSection'
import styles from './StockSection.module.scss'
import { IStockThingSectionProps, StockThingSection } from './StockThingSection'

export interface IStockSection {
  stockThing?: IStockThingSectionProps
  stockEventList?: IStockEventItemProps[]
  offerId: string
  offerStatus: OfferStatus
}

const StockSection = ({
  stockThing,
  stockEventList,
  offerId,
  offerStatus,
}: IStockSection): JSX.Element => {
  const mode = useOfferWizardMode()
  const { logEvent } = useAnalytics()

  const logEditEvent = () => {
    /* istanbul ignore next: DEBT, TO FIX */
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_WIZARD_STEP_IDS.SUMMARY,
      to: OFFER_WIZARD_STEP_IDS.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.RECAP_LINK,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
      isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
      offerId: offerId,
    })
  }

  const editLink = getOfferIndividualUrl({
    offerId,
    step: OFFER_WIZARD_STEP_IDS.STOCKS,
    mode,
  })

  const hasNoStock = !stockThing && !stockEventList?.length

  const stockWarningText = hasNoStock
    ? 'Vous n’avez aucun stock renseigné.'
    : // @ts-expect-error Other OfferStatus make stockWarningText be undefined wich is expected
      {
        [OfferStatus.SOLD_OUT]: 'Votre stock est épuisé.',
        [OfferStatus.EXPIRED]: 'Votre stock est expiré.',
      }[offerStatus]

  return (
    <>
      <SummaryLayout.Section
        title="Stocks et prix"
        editLink={editLink}
        onLinkClick={logEditEvent}
        aria-label="Modifier stock et prix"
      >
        {stockWarningText && (
          <SummaryLayout.Row
            className={styles['stock-section-warning']}
            description={stockWarningText}
          />
        )}
        {stockThing && <StockThingSection {...stockThing} />}
        {stockEventList && <StockEventSection stocks={stockEventList} />}
      </SummaryLayout.Section>
    </>
  )
}

export default StockSection
