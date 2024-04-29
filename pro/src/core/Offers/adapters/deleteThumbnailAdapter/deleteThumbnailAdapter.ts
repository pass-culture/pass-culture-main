import { api } from 'apiClient/api'

type DeleteThumbnailAdapter = Adapter<number, null, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message:
    'Une erreur est survenue lors de la suppression de votre image. Merci de réessayer plus tard.',
  payload: null,
}

export const deleteThumbnailAdapter: DeleteThumbnailAdapter = async (
  offerId: number
) => {
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
