/* istanbul ignore file */
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from 'components/IndividualOffer/IndividualOfferLayout/IndividualOfferLayout'
import { UsefulInformationsSummaryScreen } from 'components/IndividualOffer/UsefulInformationsSummaryScreen/UsefulInformationsSummary'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { ActionBar } from 'pages/IndividualOffer/components/ActionBar/ActionBar'
import { Spinner } from 'ui-kit/Spinner/Spinner'

const UsefulInformationsSummary = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer } = useIndividualOfferContext()

  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout title="Récapitulatif" offer={offer} mode={mode}>
      <UsefulInformationsSummaryScreen offer={offer} />
      <ActionBar step={OFFER_WIZARD_STEP_IDS.SUMMARY} isDisabled={false} />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = UsefulInformationsSummary
