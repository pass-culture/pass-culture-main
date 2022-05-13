import * as pcapi from 'repository/pcapi/pcapi'

import { setFeatures, setIsInitialized } from './actions'

export const loadFeatures = () => dispatch => {
  pcapi.loadFeatures().then(features => {
    dispatch(setFeatures(features))
    dispatch(setIsInitialized())
  })
}
