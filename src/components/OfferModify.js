import React, { Component } from 'react'
import { connect } from 'react-redux'
import { createSelector } from 'reselect'

import DeleteButton from './DeleteButton'
import List from './List'
import OfferForm from './OfferForm'
import PriceForm from './PriceForm'
import PriceItem from './PriceItem'
import SellerFavoriteItem from './SellerFavoriteItem'
import SellerFavoriteForm from './SellerFavoriteForm'
import SubmitButton from '../components/SubmitButton'
import WorkItem from './WorkItem'
import { assignData } from '../reducers/data'
import { NEW } from '../utils/config'

class OfferModify extends Component {
  onModifyClick = () => {
    this.props.assignData({ modifyOffer: null })
  }
  render () {
    const { id,
      modifyOffer,
      sellersFavorites,
      prices,
      work
    } = this.props
    return (
      <div className='offer-modify p2'>

        <div className='h2 mt2 mb2'> Offre </div>
        <WorkItem extraClass='mb2' {...work} />
        <OfferForm {...this.props} {...modifyOffer} />
        <SubmitButton getBody={form => form.offersById[id]}
          getIsDisabled={form =>
            !form ||
            !form.offersById ||
            !form.offersById[id] ||
            (
              !form.offersById[id].description &&
              !form.offersById[id].name
            )
          }
          getOptimistState={(state, action) => {
            const modifyOffer = Object.assign({ id: NEW,
              work
            }, action.config.body)
            return { offers: state.offers.concat(modifyOffer) }
          }}
          method={id ? 'PUT' : 'POST'}
          path='offers'
          text={id ? 'Modifer' : 'Enregistrer'}
          onClick={modifyOffer && id && this.onModifyClick}
        />

        <div className='sep mt2 mb2' />

        <List className='mb1'
          ContentComponent={SellerFavoriteItem}
          elements={sellersFavorites}
          extra={{ offerId: id }}
          FormComponent={SellerFavoriteForm}
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
              !form.sellersFavoritesById[NEW].comment
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
          isWrap
          path='sellersFavorites'
          title='Coups de Coeur' />

        <div className='sep mb2' />

        <List className='mb1'
          ContentComponent={PriceItem}
          elements={prices}
          extra={{ offerId: id }}
          FormComponent={PriceForm}
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
              !form.pricesById[NEW].groupSize ||
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
          isWrap
          path='prices'
          title='Prix' />

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

OfferModify.defaultProps = {
  id: NEW
}

const getModifyOffer = createSelector(state => state.data.offers,
  (state, ownProps) => ownProps.work.id,
  (offers, workId) => offers.find(offer => offer.workId === workId))

export default connect((state, ownProps) =>
  ({
    modifyOffer: getModifyOffer(state, ownProps),
    prices: state.data.prices || ownProps.prices,
    sellersFavorites: state.data.sellersFavorites || ownProps.sellersFavorites
  }),
  { assignData }
)(OfferModify)
