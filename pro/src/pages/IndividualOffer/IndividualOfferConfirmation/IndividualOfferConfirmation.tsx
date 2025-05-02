import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from 'components/IndividualOffer/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from 'components/IndividualOffer/IndividualOfferLayout/utils/getTitle'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { IndividualOfferConfirmationScreen } from './components/IndividualOfferConfirmationScreen'

export const IndividualOfferConfirmation = (): JSX.Element => {
  const mode = useOfferWizardMode()
  const { offer } = useIndividualOfferContext()

  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout
      withStepper={false}
      offer={offer}
      title={getTitle(mode)}
      mode={mode}
    >
      <IndividualOfferConfirmationScreen offer={offer} />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferConfirmation
