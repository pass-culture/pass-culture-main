import * as pcapi from 'repository/pcapi/pcapi'

import { setIsInitialized, setFeatures } from './actions'

export const loadFeatures = () => dispatch => {
  pcapi.loadFeatures().then(features => {
    dispatch(setFeatures(features))
    dispatch(setIsInitialized())
  })
}
