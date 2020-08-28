import { failData } from '../../reducers/data/actionCreators'
import { API_ERROR } from './errorCodes'

export function handleApiError(reducer, payload, config) {
  const [data, dispatch] = reducer
  const state = { data }
  const { handleFail } = config

  payload['error_type'] = API_ERROR
  const failAction = failData(payload, config)
  dispatch(failAction)

  if (handleFail) {
    const action = { config, payload, type: failAction.type }
    handleFail(state, action)
  }
}

export default handleApiError
