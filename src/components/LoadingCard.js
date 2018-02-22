import React from 'react'

import Loading from './Loading'

const LoadingCard = props => {
  return (
    <div className='card flex items-center justify-center'>
      <Loading {...props} />
    </div>
  )
}

export default LoadingCard
