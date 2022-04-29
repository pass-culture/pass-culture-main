export type AdapterSuccess<T> = {
  isOk: true
  message: string | null
  payload: T
}

export type AdapterFailure<T> = {
  isOk: false
  message: string
  payload: T
}

export type Adapter<Params, SuccessPayload, FailurePayload> = (
  params: Params
) => Promise<AdapterSuccess<SuccessPayload> | AdapterFailure<FailurePayload>>
