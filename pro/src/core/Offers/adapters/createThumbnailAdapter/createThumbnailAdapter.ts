import { api } from 'apiClient/api'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { IndividualOfferImage } from 'core/Offers/types'

interface Params extends OnImageUploadArgs {
  offerId: number
}

type CreateThumbnailAdapter = Adapter<Params, IndividualOfferImage, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de l’envoi de votre image',
  payload: null,
}

export const createThumbnailAdapter: CreateThumbnailAdapter = async ({
  offerId,
  imageFile,
  credit,
  cropParams,
}) => {
  try {
    const response = await api.createThumbnail({
      // TODO This TS error will be removed when spectree is updated to the latest
      // version (dependant on Flask update) which will include files in the generated schema
      // @ts-expect-error
      thumb: imageFile,
      credit: credit ?? '',
      croppingRectHeight: cropParams?.height,
      croppingRectWidth: cropParams?.width,
      croppingRectX: cropParams?.x,
      croppingRectY: cropParams?.y,
      offerId,
    })

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
