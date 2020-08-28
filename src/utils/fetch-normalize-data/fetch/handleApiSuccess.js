import { successData } from '../reducers/data/actionCreators'

export function handleApiSuccess(reducer, payload, config) {
  const [data, dispatch] = reducer
  const state = { data }
  const { handleSuccess } = config

  const successAction = successData(payload, config)
  dispatch(successAction)

  if (handleSuccess) {
    const action = { config, payload, type: successAction.type }
    handleSuccess(state, action)
  }
}

export default handleApiSuccess
