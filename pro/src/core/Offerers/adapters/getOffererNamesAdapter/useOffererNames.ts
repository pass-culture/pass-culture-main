import { api } from 'apiClient/api'
import { OffererName } from 'core/Offerers/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { useAdapter } from 'hooks'
import { dehumanizeId } from 'utils/dehumanize'

type TGetOffererNamesAdapter = Adapter<void, OffererName[], OffererName[]>

const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

type OffererNamesAdapterGetterName = (
  isAdmin?: boolean,
  offererId?: string | null
) => TGetOffererNamesAdapter
const getOffererNamesAdapter: OffererNamesAdapterGetterName = (
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
      const dehumanizedId = offererId ? dehumanizeId(offererId) : undefined
      const response = await api.listOfferersNames(
        null, // validated
        null, // validatedForUser
        isAdmin ? dehumanizedId : null // offererId
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
  return useAdapter<OffererName[], OffererName[]>(adapter)
}

export default useGetOffererNames
