/* istanbul ignore file: DEBT, TO FIX */

import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { IndivualOfferLayout } from 'components/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { StocksSummaryScreen } from 'components/IndividualOffer/StocksSummaryScreen/StocksSummaryScreen'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { ActionBar } from 'pages/IndividualOffer/components/ActionBar/ActionBar'
import { Spinner } from 'ui-kit/Spinner/Spinner'

const StocksSummary = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer } = useIndividualOfferContext()

  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndivualOfferLayout title="Récapitulatif" offer={offer} mode={mode}>
      <StocksSummaryScreen />
      <ActionBar step={OFFER_WIZARD_STEP_IDS.SUMMARY} isDisabled={false} />
    </IndivualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = StocksSummary
