import { compose } from 'redux'
import get from 'lodash.get'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import BookThisButton from './BookThisButton'
import { getPriceRangeFromStocks } from '../../../../helpers'
import currentRecommendation from '../../../../selectors/currentRecommendation'

export const getLinkDestination = match => {
  const isValid = match && typeof match === 'object' && match.params
  if (!isValid) {
    throw new Error('Invalid match parameter')
  }

  const offerId = get(match, 'params.offerId', null)
  if (!offerId) {
    throw new Error('Missing offerId parameter')
  }

  let baseURL = `/decouverte/${offerId}`

  const mediationId = get(match, 'params.mediationId', null)
  if (mediationId) baseURL = `${baseURL}/${mediationId}`
  baseURL = `${baseURL}/booking`

  return baseURL
}

export const getPriceValue = (state, params) => {
  const isValidState =
    state && typeof state === 'object' && !Array.isArray(state)
  const isValidParams =
    params && typeof params === 'object' && !Array.isArray(params)
  if (!isValidState || !isValidParams) {
    throw new Error('Invalid function parameters')
  }
  const { mediationId, offerId } = params
  const recommendation = currentRecommendation(state, offerId, mediationId)
  if (!recommendation) return []
  const stocks = get(recommendation, 'offer.stocks')
  return getPriceRangeFromStocks(stocks)
}

export const mapStateToProps = (state, { match, location }) => {
  const { params } = match
  const { search: destinationSearch } = location
  const destinationPathname = getLinkDestination(match)
  const priceValue = getPriceValue(state, params)
  return {
    destinationPathname,
    destinationSearch,
    priceValue,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(BookThisButton)
