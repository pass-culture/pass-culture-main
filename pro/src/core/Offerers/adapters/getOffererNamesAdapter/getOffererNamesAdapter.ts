import { api } from 'apiClient/api'
import { TOffererName } from 'core/Offerers/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { dehumanizeId } from 'utils/dehumanize'

interface IParams {
  offererId?: string
}
type TGetOffererNamesAdapter = Adapter<IParams, TOffererName[], TOffererName[]>
const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

const getOffererNamesAdapter: TGetOffererNamesAdapter = async ({
  offererId,
}) => {
  let dehumanizedId = undefined
  if (offererId != undefined) dehumanizedId = dehumanizeId(offererId)
  try {
    const response = await api.listOfferersNames(
      null, // validated
      null, // validatedForUser
      dehumanizedId
    )

    return {
      isOk: true,
      message: null,
      payload: response.offerersNames,
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

export default getOffererNamesAdapter
