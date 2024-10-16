import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { IndivualOfferLayout } from 'components/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { getTitle } from 'components/IndividualOffer/IndivualOfferLayout/utils/getTitle'
import { IndividualOfferConfirmationScreen } from 'pages/IndividualOfferWizard/Confirmation/IndividualOfferConfirmationScreen/IndividualOfferConfirmationScreen'
import { Spinner } from 'ui-kit/Spinner/Spinner'

export const Confirmation = (): JSX.Element => {
  const mode = useOfferWizardMode()
  const { offer } = useIndividualOfferContext()

  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndivualOfferLayout
      withStepper={false}
      offer={offer}
      title={getTitle(mode)}
      mode={mode}
    >
      <IndividualOfferConfirmationScreen offer={offer} />
    </IndivualOfferLayout>
  )
}

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Confirmation
