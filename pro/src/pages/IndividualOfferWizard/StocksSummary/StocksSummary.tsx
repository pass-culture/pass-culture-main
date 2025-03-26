/* istanbul ignore file: DEBT, TO FIX */

import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from 'components/IndividualOffer/IndividualOfferLayout/IndividualOfferLayout'
import { StocksSummaryScreen } from 'components/IndividualOffer/StocksSummaryScreen/StocksSummaryScreen'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { ActionBar } from 'pages/IndividualOffer/components/ActionBar/ActionBar'
import { Spinner } from 'ui-kit/Spinner/Spinner'

const StocksSummary = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer } = useIndividualOfferContext()

  return (
    <IndividualOfferLayout title="Récapitulatif" offer={offer} mode={mode}>
      {offer === null ? (
        <Spinner />
      ) : (
        <>
          <StocksSummaryScreen />
          <ActionBar step={OFFER_WIZARD_STEP_IDS.SUMMARY} isDisabled={false} />
        </>
      )}
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = StocksSummary
