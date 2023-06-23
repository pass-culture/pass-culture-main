import { AttachImageResponseModel } from 'apiClient/v1'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import * as pcapi from 'repository/pcapi/pcapi'

interface Params extends OnImageUploadArgs {
  offerId: number
}

type PayloadSuccess = AttachImageResponseModel
type PayloadFailure = null

export type PostCollectiveOfferImageAdapter = Adapter<
  Params,
  PayloadSuccess,
  PayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: "Une erreur est survenue lors de l'envoi de votre image",
  payload: null,
}

const postCollectiveOfferImageAdapter: PostCollectiveOfferImageAdapter =
  async ({ offerId, imageFile, credit, cropParams }) => {
    try {
      const response = await pcapi.postCollectiveOfferImage(
        offerId,
        imageFile,
        credit,
        undefined,
        cropParams?.x,
        cropParams?.y,
        cropParams?.height,
        cropParams?.width
      )

      return {
        isOk: true,
        message: '',
        payload: response,
      }
    } catch {
      return FAILING_RESPONSE
    }
  }

export default postCollectiveOfferImageAdapter
