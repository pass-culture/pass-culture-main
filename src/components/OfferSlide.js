import React from 'react'

import Icon from './Icon'
import { API_URL } from '../utils/config'

const OfferSlide = ({ id,
  name,
  prices,
  sellersFavorites,
  work
}) => {
  return (
    <div>
      <img alt=''
        className='offerPicture'
        src={`${API_URL}/thumbs/${work.id}`} />
      {
        sellersFavorites && sellersFavorites.length>0 &&
        <Icon name='favorite-outline' />
      }
      {
        prices.filter(p => p.groupSize>1).length>0 &&
        <Icon name='error' />
      }
      { prices.sort((p1, p2) => p1.value > p2.value)[0].value }&nbsp;€&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; à {(20-id)*15}m
      <div className='offerName'>
        { name || work.name }
      </div>
    </div>
  )
}

export default OfferSlide
