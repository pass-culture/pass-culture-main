import { fetchToSuccessOrFailData } from './fetch/fetchToSuccessOrFailData'
import { _requestData } from './reducers/data/actionCreators'

export const requestData = config => (dispatch, getState, defaultConfig) => {
  const { data } = getState()
  const reducer = [data, dispatch]
  const fetchConfig = { ...defaultConfig, ...config }
  dispatch(_requestData(config))
  return fetchToSuccessOrFailData(reducer, fetchConfig)
}
