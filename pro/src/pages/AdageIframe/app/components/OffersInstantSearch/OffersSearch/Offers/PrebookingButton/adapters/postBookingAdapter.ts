import { apiAdage } from 'apiClient/api'
import { hasErrorCode } from 'utils/error'

type PostBookingAdapter = Adapter<number, null, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message:
    'Impossible de préréserver cette offre.\nVeuillez contacter le support',
  payload: null,
}

const ERROR_RESPONSE: Record<string, any> = {
  WRONG_UAI_CODE: {
    isOk: false,
    message: 'Cette offre n’est pas préréservable par votre établissement',
    payload: null,
  },
  UNKNOWN_EDUCATIONAL_INSTITUTION: {
    isOk: false,
    message:
      'Votre établissement scolaire n’est pas recensé dans le dispositif pass culture',
    payload: null,
  },
}

export const postBookingAdapater: PostBookingAdapter = async stockId => {
  try {
    await apiAdage.bookCollectiveOffer({ stockId })

    return {
      isOk: true,
      message: 'Votre préréservation a été effectuée avec succès',
      payload: null,
    }
  } catch (error) {
    if (hasErrorCode(error)) {
      return ERROR_RESPONSE[error.body.code]
    }

    return FAILING_RESPONSE
  }
}
