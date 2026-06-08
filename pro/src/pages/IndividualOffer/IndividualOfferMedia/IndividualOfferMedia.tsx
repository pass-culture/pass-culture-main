import type { VideoData } from '@/apiClient/v1/new'
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
        // TODO (tpommellet): remove once `IndividualOfferContext` has been migrated to the new offer model
        initialVideoData={offer.videoData as VideoData}
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
