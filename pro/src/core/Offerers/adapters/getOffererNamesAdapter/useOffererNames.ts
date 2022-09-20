import { api } from 'apiClient/api'
import { TOffererName } from 'core/Offerers/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { useAdapter } from 'hooks'

type TGetOffererNamesAdapter = Adapter<void, TOffererName[], TOffererName[]>

const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

type TOffererNamesAdapterGetterName = (
  isAdmin?: boolean,
  offererId?: string | null
) => TGetOffererNamesAdapter
const getOffererNamesAdapter: TOffererNamesAdapterGetterName = (
  isAdmin = false,
  offererId = null
) => {
  const emptyOffererNamesAdapter: TGetOffererNamesAdapter = async () => {
    return {
      isOk: true,
      message: null,
      payload: [],
    }
  }

  const offererNamesAdapter: TGetOffererNamesAdapter = async () => {
    try {
      const response = await api.listOfferersNames(
        null, // validated
        null, // validatedForUser
        isAdmin ? offererId : null // offererId
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
  return isAdmin && !offererId ? emptyOffererNamesAdapter : offererNamesAdapter
}

interface UseAdapterArgs {
  isAdmin?: boolean
  offererId?: string | null
}
const useGetOffererNames = ({
  isAdmin = false,
  offererId = null,
}: UseAdapterArgs) => {
  const adapter = getOffererNamesAdapter(isAdmin, offererId)
  return useAdapter<TOffererName[], TOffererName[]>(adapter)
}

export default useGetOffererNames
