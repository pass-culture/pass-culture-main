type Adapter<Params, Payload> = (params: Params) => Promise<{
  isOk: boolean
  message: string | null
  payload: Payload
}>
