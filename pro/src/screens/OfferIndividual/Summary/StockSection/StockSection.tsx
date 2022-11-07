import React from 'react'

import { OfferBreadcrumbStep } from 'components/OfferBreadcrumb'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { SummaryLayout } from 'components/SummaryLayout'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'

import { IStockEventItemProps, StockEventSection } from './StockEventSection'
import { IStockThingSectionProps, StockThingSection } from './StockThingSection'

export interface IStockSection {
  stockThing?: IStockThingSectionProps
  stockEventList?: IStockEventItemProps[]
  offerId: string
}

const StockSection = ({
  stockThing,
  stockEventList,
  offerId,
}: IStockSection): JSX.Element => {
  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')
  const mode = useOfferWizardMode()
  const { logEvent } = useAnalytics()

  const logEditEvent = () => {
    /* istanbul ignore next: DEBT, TO FIX */
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OfferBreadcrumbStep.SUMMARY,
      to: OfferBreadcrumbStep.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.RECAP_LINK,
      isEdition: mode === OFFER_WIZARD_MODE.EDITION,
      isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
      offerId: offerId,
    })
  }

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

  return (
    <>
      <SummaryLayout.Section
        title="Stocks et prix"
        editLink={editLink}
        onLinkClick={logEditEvent}
      >
        {stockThing && <StockThingSection {...stockThing} />}
        {stockEventList && <StockEventSection stocks={stockEventList} />}
      </SummaryLayout.Section>
    </>
  )
}

export default StockSection
