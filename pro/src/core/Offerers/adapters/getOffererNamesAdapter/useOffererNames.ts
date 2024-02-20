import { api } from 'apiClient/api'
import { GetOffererNameResponseModel } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { useAdapter } from 'hooks'

type GetOffererNamesAdapter = Adapter<
  void,
  GetOffererNameResponseModel[],
  GetOffererNameResponseModel[]
>

const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

type OffererNamesAdapterGetterName = (
  isAdmin?: boolean,
  offererId?: string | null
) => GetOffererNamesAdapter

const getOffererNamesAdapter: OffererNamesAdapterGetterName = (
  isAdmin = false,
  offererId = null
) => {
  const emptyOffererNamesAdapter: GetOffererNamesAdapter = () =>
    Promise.resolve({
      isOk: true,
      message: null,
      payload: [],
    })

  const offererNamesAdapter: GetOffererNamesAdapter = async () => {
    try {
      const response = await api.listOfferersNames(
        null, // validated
        null, // validatedForUser
        isAdmin && offererId ? parseInt(offererId) : null // offererId
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
  return useAdapter<
    GetOffererNameResponseModel[],
    GetOffererNameResponseModel[]
  >(adapter)
}

export default useGetOffererNames
