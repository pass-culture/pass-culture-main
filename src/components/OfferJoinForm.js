import React from 'react'
import { connect } from 'react-redux'

import List from './List'
import PriceForm from './PriceForm'
import PriceItem from './PriceItem'
import FavoriteItem from './FavoriteItem'
import FavoriteForm from './FavoriteForm'
import { NEW } from '../utils/config'

const OfferJoinForm = ({ id, prices, venuesFavorites }) => {
  return (
    <div>
      <div className='sep mt2 mb2' />
      <List className='mb1'
        ContentComponent={PriceItem}
        elements={prices}
        extra={{ offerId: id }}
        FormComponent={PriceForm}
        getBody={form => Object.assign({ offerId: id }, form.pricesById[NEW])}
        getIsDisabled={form =>
          !form ||
          !form.pricesById ||
          !form.pricesById[NEW] ||
          (
            !form.pricesById[NEW].groupSize ||
            !form.pricesById[NEW].value
          )
        }
        getOptimistState={(state, action) => {
          let optimistPrices = [action.config.body]
          if (prices) {
            optimistPrices = optimistPrices.concat(prices)
          }
          return {
            prices: optimistPrices
          }
        }}
        getSuccessState={(state, action) => {
          const offerIds = state.offers.map(({ id }) => id)
          const offerIndex = offerIds.indexOf(id)
          const nextOffers = [...state.offers]
          nextOffers[offerIndex] = Object.assign({}, nextOffers[offerIndex], {
            prices: [action.data].concat(nextOffers[offerIndex].prices)
          })
          // on success we need to make this buffer
          // null again in order to catch the new refreshed ownProps.prices
          return { offers: nextOffers, prices: null }
        }}
        isWrap
        path='prices'
        title='Prix' />

      <div className='sep mb2' />

      <List className='mb1'
        ContentComponent={FavoriteItem}
        elements={venuesFavorites}
        extra={{ offerId: id }}
        FormComponent={FavoriteForm}
        getBody={form => Object.assign({ offerId: id },
          form.venuesFavoritesById[NEW])}
        getIsDisabled={form =>
          !form ||
          !form.venuesFavoritesById ||
          !form.venuesFavoritesById[NEW] ||
          (
            !form.venuesFavoritesById[NEW].comment
          )
        }
        getOptimistState={(state, action) => {
          let optimistSellersFavorites = [action.config.body]
          if (venuesFavorites) {
            optimistSellersFavorites = optimistSellersFavorites.concat(venuesFavorites)
          }
          return {
            venuesFavorites: optimistSellersFavorites
          }
        }}
        getSuccessState={(state, action) => {
          const offerIds = state.offers.map(({ id }) => id)
          const offerIndex = offerIds.indexOf(id)
          const nextOffers = [...state.offers]
          nextOffers[offerIndex] = Object.assign({}, nextOffers[offerIndex], {
            venuesFavorites: [action.data].concat(nextOffers[offerIndex].venuesFavorites)
          })
          // on success we need to make this buffer
          // null again in order to catch the new refreshed ownProps.venuesFavorites
          return { offers: nextOffers, venuesFavorites: null }
        }}
        isWrap
        path='venuesFavorites'
        title='Coups de Coeur' />
    </div>
  )
}

export default connect((state, ownProps) =>
  ({
    prices: state.data.prices || ownProps.prices,
    venuesFavorites: state.data.venuesFavorites || ownProps.venuesFavorites
  })
)(OfferJoinForm)
