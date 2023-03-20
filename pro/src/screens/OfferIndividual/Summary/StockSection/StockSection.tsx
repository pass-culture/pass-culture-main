import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { SummaryLayout } from 'components/SummaryLayout'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'

import { RecurrenceSection } from './RecurrenceSection'
import { StockEventSection } from './StockEventSection'
import styles from './StockSection.module.scss'
import { StockThingSection } from './StockThingSection'

export interface IStockSection {
  offer: IOfferIndividual
}

const StockSection = ({ offer }: IStockSection): JSX.Element => {
  const mode = useOfferWizardMode()
  const { logEvent } = useAnalytics()
  const isRecurrenceActive = useActiveFeature('WIP_RECURRENCE')

  const logEditEvent = () => {
    /* istanbul ignore next: DEBT, TO FIX */
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_WIZARD_STEP_IDS.SUMMARY,
      to: OFFER_WIZARD_STEP_IDS.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.RECAP_LINK,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
      isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
      offerId: offer.id,
    })
  }

  const editLink = getOfferIndividualUrl({
    offerId: offer.id,
    step: OFFER_WIZARD_STEP_IDS.STOCKS,
    mode,
  })

  const hasNoStock = offer.stocks.length === 0

  const stockWarningText = hasNoStock
    ? 'Vous n’avez aucun stock renseigné.'
    : // @ts-expect-error Other OfferStatus make stockWarningText be undefined wich is expected
      {
        [OfferStatus.SOLD_OUT]: 'Votre stock est épuisé.',
        [OfferStatus.EXPIRED]: 'Votre stock est expiré.',
      }[offer.status]

  return (
    <>
      <SummaryLayout.Section
        title={offer.isEvent ? 'Dates et capacité' : 'Stocks et prix'}
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

        {offer.isEvent ? (
          isRecurrenceActive ? (
            <RecurrenceSection offer={offer} />
          ) : (
            <StockEventSection offer={offer} />
          )
        ) : (
          <StockThingSection offer={offer} />
        )}
      </SummaryLayout.Section>
    </>
  )
}

export default StockSection
