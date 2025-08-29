/* istanbul ignore file */

import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { INDIVIDUAL_OFFER_WIZARD_STEP_IDS } from '@/commons/core/Offers/constants'
import { useCurrentUser } from '@/commons/hooks/useCurrentUser'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferSummaryPracticalInfosScreen } from './components/IndividualOfferSummaryPracticalInfosScreen'

const IndividualOfferSummaryPracticalInfos = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer } = useIndividualOfferContext()
  const { currentUser } = useCurrentUser()

  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout title="Récapitulatif" offer={offer} mode={mode}>
      <IndividualOfferSummaryPracticalInfosScreen
        offer={offer}
        currentUser={currentUser}
      />
      <ActionBar
        step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY}
        isDisabled={false}
      />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferSummaryPracticalInfos
