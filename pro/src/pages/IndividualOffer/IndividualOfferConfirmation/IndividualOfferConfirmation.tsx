import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferConfirmationScreen } from './components/IndividualOfferConfirmationScreen'

export const IndividualOfferConfirmation = (): JSX.Element => {
  const { offer } = useIndividualOfferContext()

  if (offer === null) {
    return <Spinner />
  }

  return <IndividualOfferConfirmationScreen offer={offer} />
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferConfirmation
