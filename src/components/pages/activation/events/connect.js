import get from 'lodash.get'
import { requestData } from 'pass-culture-shared'

import { parseActivationOffers } from './utils'

export const mapStateToProps = state => {
  let offers = get(state, 'data.offers') || []
  offers = parseActivationOffers(offers)
  return { offers }
}

export const mapDispatchToProps = dispatch => ({
  getAllActivationOffers: (handleFail, handleSuccess) => {
    const body = {}
    const requestMethod = 'GET'
    const requestPath = 'offers/activation'
    const options = { body, handleFail, handleSuccess }
    dispatch(requestData(requestMethod, requestPath, options))
  },
})

export default mapDispatchToProps
