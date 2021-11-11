import { failData } from '../../reducers/data/actionCreators'
import { SERVER_ERROR } from './errorCodes'

export const GLOBAL_SERVER_ERROR = 'Server error. Try to refresh the page.'

export function handleServerError(reducer, error, config) {
  const [data, dispatch] = reducer
  const state = { data }
  const { handleFail } = config
  const globalServerError = config.globalServerError || GLOBAL_SERVER_ERROR

  const errors = [
    {
      global: [globalServerError],
    },
    {
      data: [String(error)],
    },
  ]

  const payload = {
    error_type: SERVER_ERROR,
    errors,
    ok: false,
    status: 500,
  }

  const failAction = failData(payload, config)
  dispatch(failAction)

  if (handleFail) {
    const action = { config, payload, type: failAction.type }
    handleFail(state, action)
  }
}
