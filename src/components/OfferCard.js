import React from 'react'

import SellerFavoriteItem from './SellerFavoriteItem'
import { API_URL } from '../utils/config'

const OfferCard = ({ id,
  name,
  sellersFavorites,
  work
}) => {
  return (
    <div className='offer-card flex items-center justify-center'>
      <div className='offer-card__content relative' style={{
        backgroundImage: `url(${API_URL}/thumbs/${work.id})`,
        backgroundRepeat: 'no-repeat',
        backgroundSize: 'cover'
      }}>
        <div className='offer-card__content__info absolute bottom-0 left-0 right-0 m2 p1'>
          à {(20-id)*15}m
          {
            sellersFavorites && sellersFavorites.map((sellersFavorite, index) =>
              <SellerFavoriteItem key={index} {...sellersFavorite} />
            )
          }
        </div>
      </div>
    </div>
  )
}

export default OfferCard
