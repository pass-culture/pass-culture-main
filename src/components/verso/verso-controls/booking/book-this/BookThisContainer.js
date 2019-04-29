import { compose } from 'redux'
import get from 'lodash.get'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import BookThis from './BookThis'
import { getPriceRangeFromStocks } from '../../../../../helpers'
import currentRecommendation from '../../../../../selectors/currentRecommendation'

export const getLinkDestination = (url, search) => {
  const isValid = url && typeof url === 'string'
  if (!isValid) {
    throw new Error('Invalid url parameter')
  }
  const strippedUrl = url.replace(/\/$/, '')
  const result = `${strippedUrl}/booking${search || ''}`
  return result
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
  const { params, url } = match
  const { search } = location
  const linkDestination = getLinkDestination(url, search)
  const priceValue = getPriceValue(state, params)
  return {
    linkDestination,
    priceValue,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(BookThis)
