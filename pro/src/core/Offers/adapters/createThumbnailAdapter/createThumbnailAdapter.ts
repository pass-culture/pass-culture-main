import { IOfferIndividualImage } from 'core/Offers/types'
import { IOnImageUploadArgs } from 'new_components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import * as pcapi from 'repository/pcapi/pcapi'

interface Params extends IOnImageUploadArgs {
  offerId: string
}

export type TCreateThumbnailAdapter = Adapter<
  Params,
  IOfferIndividualImage,
  null
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: "Une erreur est survenue lors de l'envoi de votre image",
  payload: null,
}

const createThumbnailAdapter: TCreateThumbnailAdapter = async ({
  offerId,
  imageData,
  credit,
  cropParams,
}) => {
  try {
    const response = await pcapi.postThumbnail(
      offerId,
      credit,
      imageData,
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
        url: response.url,
        credit: response.credit,
      },
    }
  } catch {
    return FAILING_RESPONSE
  }
}

export default createThumbnailAdapter
