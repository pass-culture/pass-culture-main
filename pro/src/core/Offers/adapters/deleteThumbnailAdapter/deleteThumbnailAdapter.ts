import { api } from 'apiClient/api'

interface Params {
  offerId: string
}

export type TDeleteThumbnailAdapter = Adapter<Params, null, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la suppression de votre image',
  payload: null,
}

const deleteThumbnailAdapter: TDeleteThumbnailAdapter = async ({ offerId }) => {
  try {
    await api.deleteThumbnail(offerId)
    return {
      isOk: true,
      message: '',
      payload: null,
    }
  } catch {
    return FAILING_RESPONSE
  }
}

export default deleteThumbnailAdapter
