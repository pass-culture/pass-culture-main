import React from 'react'
import { connect } from 'react-redux'

import List from './List'
import PriceForm from './PriceForm'
import PriceItem from './PriceItem'
import SellerFavoriteItem from './SellerFavoriteItem'
import SellerFavoriteForm from './SellerFavoriteForm'
import { NEW } from '../utils/config'

const OfferJoinForm = ({ id, prices, sellersFavorites }) => {
  return (
    <div>
      <div className='sep mt2 mb2' />
      <List className='mb1'
        ContentComponent={PriceItem}
        elements={prices}
        extra={{ offerId: id }}
        FormComponent={PriceForm}
        getBody={form => Object.assign({
          offerId: id
        }, form.pricesById[NEW])}
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
        getSuccessState={state =>
          // on success we need to make this buffer
          // null again in order to catch the new refreshed ownProps.prices
          ({ prices: null })
        }
        isWrap
        path='prices'
        title='Prix' />

      <div className='sep mb2' />

      <List className='mb1'
        ContentComponent={SellerFavoriteItem}
        elements={sellersFavorites}
        extra={{ offerId: id }}
        FormComponent={SellerFavoriteForm}
        getBody={form => 
          Object.assign({
            offerId: id
          }, form.sellersFavoritesById[NEW])
        }
        getIsDisabled={form =>
          !form ||
          !form.sellersFavoritesById ||
          !form.sellersFavoritesById[NEW] ||
          (
            !form.sellersFavoritesById[NEW].comment
          )
        }
        getOptimistState={(state, action) => {
          let optimistSellersFavorites = [action.config.body]
          if (sellersFavorites) {
            optimistSellersFavorites = optimistSellersFavorites.concat(sellersFavorites)
          }
          return {
            sellersFavorites: optimistSellersFavorites
          }
        }}
        getSuccessState={state =>
          // on success we need to make this buffer
          // null again in order to catch the new refreshed ownProps.sellersFavorites
          ({ sellersFavorites: null })
        }
        isWrap
        path='sellersFavorites'
        title='Coups de Coeur' />
    </div>
  )
}

export default connect((state, ownProps) =>
  ({
    prices: state.data.prices || ownProps.prices,
    sellersFavorites: state.data.sellersFavorites || ownProps.sellersFavorites
  })
)(OfferJoinForm)
