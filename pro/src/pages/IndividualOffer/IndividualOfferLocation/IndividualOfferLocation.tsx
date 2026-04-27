import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferLocationScreen } from './components/IndividualOfferLocationScreen'

export const IndividualOfferLocation = () => {
  const { offer } = useIndividualOfferContext()

  // TODO (igabriele, 2025-08-20): Handle API error.s
  if (!offer) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout offer={offer}>
      <IndividualOfferLocationScreen offer={offer} />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferLocation
