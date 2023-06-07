import { useEffect, useState } from 'react'

type UseAdapterLoading = {
  data?: undefined
  isLoading: true
  error?: undefined
}

type UseAdapterSuccess<T> = {
  data: T
  isLoading: false
  error?: undefined
}

type UseAdapterFailure<T> = {
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
  | UseAdapterLoading
  | UseAdapterSuccess<ISuccessPayload>
  | UseAdapterFailure<IFailurePayload> => {
  const [hookResponse, setHookResponse] = useState<
    | UseAdapterLoading
    | UseAdapterSuccess<ISuccessPayload>
    | UseAdapterFailure<IFailurePayload>
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
    loadData()
  }, [])

  return hookResponse
}

export default useAdapter
