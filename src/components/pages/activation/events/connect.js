import get from 'lodash.get'
import { requestData } from 'pass-culture-shared'

import { getRouterQueryByKey } from '../../../../helpers'
import { groupOffersByCityCode, parseActivationOffers } from './utils'

export const mapStateToProps = (state, { location }) => {
  let offers = get(state, 'data.offers') || []
  offers = parseActivationOffers(offers)
  offers = groupOffersByCityCode(offers)
  const from = getRouterQueryByKey(location, 'from')
  const fromPassword = from === 'password'
  return { fromPassword, offers }
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
