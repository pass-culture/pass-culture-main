import { AttachImageResponseModel } from 'apiClient/v1'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import * as pcapi from 'repository/pcapi/pcapi'

interface Params extends OnImageUploadArgs {
  offerId: string
}

type IPayloadSuccess = AttachImageResponseModel
type IPayloadFailure = null

export type PostCollectiveOfferImageAdapter = Adapter<
  Params,
  IPayloadSuccess,
  IPayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: "Une erreur est survenue lors de l'envoi de votre image",
  payload: null,
}

const postCollectiveOfferTemplateImageAdapter: PostCollectiveOfferImageAdapter =
  async ({ offerId, imageFile, credit, cropParams }) => {
    try {
      const response = await pcapi.postCollectiveOfferTemplateImage(
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

export default postCollectiveOfferTemplateImageAdapter
