import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { IndividualOfferImage } from 'core/Offers/types'
import * as pcapi from 'repository/pcapi/pcapi'

interface Params extends OnImageUploadArgs {
  offerId: number
}

type CreateThumbnailAdapter = Adapter<Params, IndividualOfferImage, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de l’envoi de votre image',
  payload: null,
}

const createThumbnailAdapter: CreateThumbnailAdapter = async ({
  offerId,
  imageFile,
  credit,
  cropParams,
}) => {
  try {
    const response = await pcapi.postThumbnail(
      offerId.toString(),
      imageFile,
      credit,
      undefined, // api don't use thumbUrl
      cropParams?.x,
      cropParams?.y,
      cropParams?.height,
      cropParams?.width
    )

    return {
      isOk: true,
      message: '',
      payload: {
        originalUrl: response.url,
        url: response.url,
        credit: response.credit ?? null,
      },
    }
  } catch {
    return FAILING_RESPONSE
  }
}

export default createThumbnailAdapter
