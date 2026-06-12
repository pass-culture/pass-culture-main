import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferExposureScreen } from './IndividualOfferExposureScreen'

export const IndividualOfferExposure = () => {
  const { offer } = useIndividualOfferContext()

  if (!offer) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout offer={offer}>
      <IndividualOfferExposureScreen offer={offer} />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferExposure
