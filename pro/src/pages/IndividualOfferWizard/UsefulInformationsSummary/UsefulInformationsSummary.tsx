/* istanbul ignore file */
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
import { ActionBar } from 'screens/IndividualOffer/ActionBar/ActionBar'
import { IndivualOfferLayout } from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { UsefulInformationsSummaryScreen } from 'screens/IndividualOffer/UsefulInformationsSummaryScreen/UsefulInformationsSummary'
import { Spinner } from 'ui-kit/Spinner/Spinner'

const UsefulInformationsSummary = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer } = useIndividualOfferContext()

  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndivualOfferLayout title="Récapitulatif" offer={offer} mode={mode}>
      <UsefulInformationsSummaryScreen offer={offer} />
      <ActionBar step={OFFER_WIZARD_STEP_IDS.SUMMARY} isDisabled={false} />
    </IndivualOfferLayout>
  )
}

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = UsefulInformationsSummary
