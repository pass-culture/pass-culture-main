import React, { Component }  from 'react'

import FormInput from './FormInput'
import FormTextarea from './FormTextarea'
import List from './List'
import PriceModify from './PriceModify'
import PriceItem from './PriceItem'
import SellerFavoriteItem from './SellerFavoriteItem'
import SellerFavoriteModify from './SellerFavoriteModify'
import SubmitButton from './SubmitButton'

const OfferModify = ({
  description,
  id,
  isEditing,
  name,
  sellersFavorites,
  thumbnailUrl,
  prices,
  work
}) => {
  return (
    <div className='offer-modify p2'>

      <FormInput className='input mt1 mb3'
        defaultValue={name}
        name='name'
        placeholder="titre de l'offre"
      />
      <div className='sep mb2' />
      <div className='offer-modify__hero flex flex-wrap items-center justify-around mb2 p1'>
        <img alt='thumbnail'
          className='offer-modify__hero__img mb1'
          src={thumbnailUrl || work.thumbnailUrl} />
        <FormTextarea className='textarea offer-modify__hero__textarea'
          defaultValue={description}
          name='description'
          placeholder="Vous pouvez écrire un description ici" >
          {description}
        </FormTextarea>
      </div>
      <button className='button button--alive mb2'>
        Soumettre
      </button>

      <div className='sep mb2' />

      <List className='mb1'
        ContentComponent={SellerFavoriteItem}
        elements={sellersFavorites}
        extra={{ offerId: id }}
        getBody={form => [{
          description: form.sellersFavoriteDescription,
          offerId: id
        }]}
        getOptimistState={(state, action) => {
          let sellersFavorites
          const offers = state.offers.map(offer => {
            if (offer.id === id) {
              sellersFavorites = action.config.body.concat(
                offer.sellersFavorites)
            }
            return offer
          })
          return { sellersFavorites }
        }}
        ModifyComponent={SellerFavoriteModify}
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
          let prices
          const offers = state.offers.map(offer => {
            if (offer.id === id) {
              prices = action.config.body.concat(
                offer.prices)
            }
            return offer
          })
          return { prices }
        }}
        ModifyComponent={PriceModify}
        path='prices'
        title='Offres' />

      <div className='sep mb2' />

    </div>
  )
}

export default OfferModify
