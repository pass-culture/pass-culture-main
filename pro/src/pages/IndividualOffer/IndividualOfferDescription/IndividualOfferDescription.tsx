import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'

import { IndividualOfferDescriptionScreen } from './components/IndividualOfferDescriptionScreen'
import { IndividualOfferDescriptionPOC } from './IndividualOfferDescriptionPOC/IndividualOfferDescriptionPOC'

const IndividualOfferDescription = (): JSX.Element | null => {
  const { offer } = useIndividualOfferContext()

  return (
    <IndividualOfferLayout offer={offer}>
      <IndividualOfferDescriptionPOC key={offer?.id} />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferDescription
