/* istanbul ignore file: DEBT, TO FIX */

import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { INDIVIDUAL_OFFER_WIZARD_STEP_IDS } from 'commons/core/Offers/constants'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from 'components/IndividualOfferLayout/IndividualOfferLayout'
import { ActionBar } from 'pages/IndividualOffer/components/ActionBar/ActionBar'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { IndividualOfferSummaryStocksCalendarScreen } from './components/IndividualOfferSummaryStocksCalendarScreen/IndividualOfferSummaryStocksCalendarScreen'
import { IndividualOfferSummaryStocksScreen } from './components/IndividualOfferSummaryStocksScreen/IndividualOfferSummaryStocksScreen'

const IndividualOfferSummaryStocks = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer } = useIndividualOfferContext()

  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout title="Récapitulatif" offer={offer} mode={mode}>
      {offer.isEvent ? (
        <IndividualOfferSummaryStocksCalendarScreen offer={offer} />
      ) : (
        <IndividualOfferSummaryStocksScreen />
      )}
      <ActionBar
        step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY}
        isDisabled={false}
      />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferSummaryStocks
