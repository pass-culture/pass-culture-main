import React, { Component } from 'react'
import { connect } from 'react-redux'

import List from './List'
import OfferForm from './OfferForm'
import OfferItem from './OfferItem'
import PriceForm from './PriceForm'
import PriceItem from './PriceItem'
import SellerFavoriteItem from './SellerFavoriteItem'
import SellerFavoriteForm from './SellerFavoriteForm'

class OfferModify extends Component {
  render () {
    const { id,
      newOffer,
      sellersFavorites,
      prices
    } = this.props
  return (
    <div className='offer-modify p2'>

      {
        /*
        newOffer
          ? <OfferItem {...this.props} {...newOffer} />
          : <OfferForm {...this.props} />
        */
      }

      <div className='sep mb2' />

      <List className='mb1'
        ContentComponent={SellerFavoriteItem}
        elements={sellersFavorites}
        extra={{ offerId: id }}
        getBody={form => [{
          description: form.description,
          offerId: id
        }]}
        getIsDisabled={form => !form.description && !form.title}
        getOptimistState={(state, action) => {
          const offer = state.offers.find(offer => offer.id === id)
          return { sellersFavorites: action.config.body.concat(
            offer.sellersFavorites) }
        }}
        FormComponent={SellerFavoriteForm}
        path='sellersFavorites'
        title='Coups de Coeur' />

      <div className='sep mb2' />

      <List className='mb1'
        ContentComponent={PriceItem}
        elements={prices}
        extra={{ offerId: id }}
        getBody={form => [Object.assign({
          offerId: id
        }, form)]}
        getOptimistState={(state, action) => {
          const offer = state.offers.find(offer => offer.id === id)
          return { prices: action.config.body.concat(offer.prices) }
        }}
        FormComponent={PriceForm}
        path='prices'
        title='Offres' />

      <div className='sep mb2' />

    </div>
  )
}
}

export default connect(state =>
  ({ newOffer: state.data.newOffer }))(OfferModify)
