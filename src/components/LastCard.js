import React from 'react'

import { API_URL } from '../utils/config'

const LastCard = props => {
  return (
    <div className='card flex items-center justify-center'>
      <div className='card__content' style={{
        backgroundImage: `url(${API_URL}/static/images/last_thumb.png)`,
        backgroundRepeat: 'no-repeat',
        backgroundSize: 'cover'
      }} />
    </div>
  )
}

export default LastCard
