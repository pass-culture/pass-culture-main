import React from 'react'
import { connect } from 'react-redux'

import List from './List'
import MediationForm from './MediationForm'
import MediationItem from './MediationItem'
import PriceForm from './PriceForm'
import PriceItem from './PriceItem'

import { NEW } from '../utils/config'

const OfferJoinForm = ({ id, prices, mediations }) => {
  return (
    <div>
      <div className="sep mt2 mb2" />
      <List
        className="mb1"
        ContentComponent={PriceItem}
        elements={prices}
        extra={{ offerId: id }}
        FormComponent={PriceForm}
        getBody={form => Object.assign({ offerId: id }, form.pricesById[NEW])}
        getIsDisabled={form =>
          !form ||
          !form.pricesById ||
          !form.pricesById[NEW] ||
          (!form.pricesById[NEW].groupSize || !form.pricesById[NEW].value)
        }
        getOptimistState={(state, action) => {
          let optimistPrices = [action.config.body]
          if (prices) {
            optimistPrices = optimistPrices.concat(prices)
          }
          return {
            prices: optimistPrices,
          }
        }}
        getSuccessState={(state, action) => {
          const offerIds = state.offers.map(({ id }) => id)
          const offerIndex = offerIds.indexOf(id)
          const nextOffers = [...state.offers]
          nextOffers[offerIndex] = Object.assign({}, nextOffers[offerIndex], {
            prices: [action.data].concat(nextOffers[offerIndex].prices),
          })
          // on success we need to make this buffer
          // null again in order to catch the new refreshed ownProps.prices
          return { offers: nextOffers, prices: null }
        }}
        isWrap
        path="prices"
        title="Prix"
      />

      <div className="sep mb2" />

      <List
        className="mb1"
        ContentComponent={MediationItem}
        elements={mediations}
        extra={{ offerId: id }}
        FormComponent={MediationForm}
        getBody={form =>
          Object.assign({ offerId: id }, form.mediationsById[NEW])
        }
        getIsDisabled={form =>
          !form ||
          !form.mediationsById ||
          !form.mediationsById[NEW] ||
          !form.mediationsById[NEW].description
        }
        getOptimistState={(state, action) => {
          let optimistSellersMediations = [action.config.body]
          if (mediations) {
            optimistSellersMediations = optimistSellersMediations.concat(
              mediations
            )
          }
          return {
            mediations: optimistSellersMediations,
          }
        }}
        getSuccessState={(state, action) => {
          const offerIds = state.offers.map(({ id }) => id)
          const offerIndex = offerIds.indexOf(id)
          const nextOffers = [...state.offers]
          nextOffers[offerIndex] = Object.assign({}, nextOffers[offerIndex], {
            mediations: [action.data].concat(nextOffers[offerIndex].mediations),
          })
          // on success we need to make this buffer
          // null again in order to catch the new refreshed ownProps.mediations
          return { offers: nextOffers, mediations: null }
        }}
        isWrap
        path="mediations"
        title="Coups de Coeur"
      />
    </div>
  )
}

export default connect((state, ownProps) => ({
  mediations: state.data.mediations || ownProps.mediations,
  prices: state.data.prices || ownProps.prices,
}))(OfferJoinForm)
