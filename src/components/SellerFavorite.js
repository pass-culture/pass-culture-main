import React from 'react'

import Icon from './Icon'

const SellerFavorite = ({ comment, tag }) => {
  return (
    <div className='seller-favorite p3 mb2 relative'>
      <div className='seller-favorite__icon absolute'>
        <Icon name='favorite-outline' />
      </div>
      <div className='mt2 mb2'>
        {comment}
        <div>
          {tag}
        </div>
      </div>
    </div>
  )
}

export default SellerFavorite
