import { api } from 'apiClient/api'

import { setFeatures, setIsInitialized } from './actions'

export const loadFeatures = () => dispatch => {
  api.listFeatures().then(features => {
    dispatch(setFeatures(features))
    dispatch(setIsInitialized())
  })
}
