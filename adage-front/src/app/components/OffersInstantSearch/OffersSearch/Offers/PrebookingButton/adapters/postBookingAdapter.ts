import { api } from 'api/api'
import { Adapter, AdapterFailure } from 'app/types'
import { hasErrorCode } from 'utils/error'

type PostBookingAdapter = Adapter<number, null, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message:
    'Impossible de préréserver cette offre.\nVeuillez contacter le support',
  payload: null,
}

const NOT_BOOKABLE_BY_USER_FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Cette offre n’est pas préréservable par votre établissement',
  payload: null,
}

export const postBookingAdapater: PostBookingAdapter = async stockId => {
  try {
    await api.postAdageIframeBookCollectiveOffer({ stockId })

    return {
      isOk: true,
      message: 'Votre préréservation a été effectuée avec succès',
      payload: null,
    }
  } catch (error) {
    if (hasErrorCode(error) && error.content.code === 'WRONG_UAI_CODE') {
      return NOT_BOOKABLE_BY_USER_FAILING_RESPONSE
    }

    return FAILING_RESPONSE
  }
}
