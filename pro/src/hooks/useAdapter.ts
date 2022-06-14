import { useEffect, useState } from 'react'

type TUseAdapterLoading = {
  data?: undefined
  isLoading: true
  error?: undefined
}

type TUseAdapterSuccess<T> = {
  data: T
  isLoading: false
  error?: undefined
}

type TUseAdapterFailure<T> = {
  data?: undefined
  isLoading: false
  error: {
    message: string
    payload: T
  }
}

const useAdapter = <ISuccessPayload, IFailurePayload>(
  getData: () => Promise<
    AdapterSuccess<ISuccessPayload> | AdapterFailure<IFailurePayload>
  >
):
  | TUseAdapterLoading
  | TUseAdapterSuccess<ISuccessPayload>
  | TUseAdapterFailure<IFailurePayload> => {
  const [hookResponse, setHookResponse] = useState<
    | TUseAdapterLoading
    | TUseAdapterSuccess<ISuccessPayload>
    | TUseAdapterFailure<IFailurePayload>
  >({ isLoading: true })

  useEffect(() => {
    async function loadData() {
      const response = await getData()
      if (response.isOk) {
        setHookResponse({
          data: response.payload,
          isLoading: false,
        })
      } else {
        setHookResponse({
          error: {
            message: response.message,
            payload: response.payload,
          },
          isLoading: false,
        })
      }
    }
    if (hookResponse.isLoading) {
      loadData()
    }
  }, [hookResponse.isLoading])

  return hookResponse
}

export default useAdapter
