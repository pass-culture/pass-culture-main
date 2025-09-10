import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferConfirmationScreen } from './components/IndividualOfferConfirmationScreen'

export const IndividualOfferConfirmation = (): JSX.Element => {
  const { offer } = useIndividualOfferContext()

  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout withStepper={false} offer={offer}>
      <IndividualOfferConfirmationScreen offer={offer} />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferConfirmation
