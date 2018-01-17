import React, { Component } from 'react'
import { connect } from 'react-redux'

import DeleteButton from './DeleteButton'
import List from './List'
import OfferForm from './OfferForm'
import OfferItem from './OfferItem'
import PriceForm from './PriceForm'
import PriceItem from './PriceItem'
import SellerFavoriteItem from './SellerFavoriteItem'
import SellerFavoriteForm from './SellerFavoriteForm'
import SubmitButton from '../components/SubmitButton'
import { assignData } from '../reducers/data'
import { NEW } from '../utils/config'

class OfferModify extends Component {
  onModifyClick = () => {
    this.props.assignData({ newOffer: null })
  }
  render () {
    const { id,
      newOffer,
      sellersFavorites,
      prices,
      work
    } = this.props
  console.log('work', work)
  return (
    <div className='offer-modify p2'>

      <div className='h2 mt2'> Offre </div>
      <div className='offer-modify__control flex items-center flex-start'>
        {
          newOffer
          ? (
            id && (
              <button className='button button--alive'
                onClick={this.onModifyClick}>
                Modifier
              </button>
            )
          )
          : <SubmitButton getBody={form => form.offersById[NEW]}
            getIsDisabled={form =>
              !form ||
              !form.offersById ||
              !form.offersById[NEW] ||
              (
                !form.offersById[NEW].description &&
                !form.offersById[NEW].name
              )
            }
            getOptimistState={(state, action) => {
              const newOffer = Object.assign({
                work
              }, action.config.body)
              return { newOffer,
                offers: state.offers.concat(newOffer)
              }
            }}
            path='offers' />
        }

      </div>
      {
        newOffer
          ? <OfferItem {...this.props} {...newOffer} />
          : <OfferForm {...this.props} />
      }

      <div className='sep mb2' />

      <List className='mb1'
        ContentComponent={SellerFavoriteItem}
        elements={sellersFavorites}
        extra={{ offerId: id }}
        getBody={form => [
          Object.assign({
            offerId: id
          }, form.sellersFavoritesById[NEW])
        ]}
        getIsDisabled={form =>
          !form ||
          !form.sellersFavoritesById ||
          !form.sellersFavoritesById[NEW] ||
          (
            !form.sellersFavoritesById[NEW].description
          )
        }
        getOptimistState={(state, action) => {
          let optimistSellersFavorites = action.config.body
          if (sellersFavorites) {
            optimistSellersFavorites = optimistSellersFavorites.concat(sellersFavorites)
          }
          return {
            sellersFavorites: optimistSellersFavorites
          }
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
        }, form.pricesById[NEW])]}
        getIsDisabled={form =>
          !form ||
          !form.pricesById ||
          !form.pricesById[NEW] ||
          (
            !form.pricesById[NEW].endDate ||
            !form.pricesById[NEW].startDate ||
            !form.pricesById[NEW].size ||
            !form.pricesById[NEW].value
          )
        }
        getOptimistState={(state, action) => {
          let optimistPrices = action.config.body
          if (prices) {
            optimistPrices = optimistPrices.concat(prices)
          }
          return {
            prices: optimistPrices
          }
        }}
        FormComponent={PriceForm}
        path='prices'
        title='Offres' />

      <div className='sep mb2' />

      <DeleteButton className='button button--alive mb2'
        collectionName='offers'
        id={id}
        text='Supprimer'
      />

    </div>
  )
}
}

export default connect((state, ownProps) =>
  ({
    newOffer: state.data.newOffer,
    prices: state.data.prices || ownProps.prices,
    sellersFavorites: state.data.sellersFavorites || ownProps.sellersFavorites
  }),
  { assignData }
)(OfferModify)
