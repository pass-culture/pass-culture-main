import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { VideoUploaderContextProvider } from './commons/context/VideoUploaderContext/VideoUploaderContext'
import { IndividualOfferMediaScreen } from './components/IndividualOfferMediaScreen'

const IndividualOfferMedia = (): JSX.Element | null => {
  const { offer } = useIndividualOfferContext()

  if (!offer) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout offer={offer}>
      <VideoUploaderContextProvider
        initialVideoData={offer.videoData}
        offerId={offer.id}
      >
        <IndividualOfferMediaScreen offer={offer} />
      </VideoUploaderContextProvider>
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferMedia
