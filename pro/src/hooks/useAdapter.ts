import { useCallback, useEffect, useState } from 'react'

type UseAdapterLoading = {
  data?: undefined
  isLoading: true
  error?: undefined
  reloadData: () => Promise<void>
}

type UseAdapterSuccess<T> = {
  data: T
  isLoading: false
  error?: undefined
  reloadData: () => Promise<void>
}

type UseAdapterFailure<T> = {
  data?: undefined
  isLoading: false
  error: {
    message: string
    payload: T
  }
  reloadData: () => Promise<void>
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
    | Omit<UseAdapterLoading, 'reloadData'>
    | Omit<UseAdapterSuccess<ISuccessPayload>, 'reloadData'>
    | Omit<UseAdapterFailure<IFailurePayload>, 'reloadData'>
  >({ isLoading: true })

  const loadData = useCallback(async () => {
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
  }, [])

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadData()
  }, [loadData])

  return {
    ...hookResponse,
    reloadData: loadData,
  }
}

export default useAdapter
