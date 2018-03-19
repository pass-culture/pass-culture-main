import classnames from 'classnames'
import React from 'react'

import Loading from './Loading'

const Recto = ({ isFullWidth,
  isLoading,
  thumbUrl
}) => {
  return (
    <div className={classnames('recto', { 'recto--small': !isFullWidth })} style={{
      backgroundImage: `url(${thumbUrl})`,
      overflowX: 'hidden ! important',
      overflowY: 'hidden ! important',
      backgroundColor: '#f8f8f8',
      backgroundSize: 'contain',
      backgroundRepeat: 'no-repeat',
      backgroundPosition: 'left top',
    }}>
      {
        isLoading && (
          <div className='recto__loading flex items-center justify-center'>
            <Loading isForceActive />
          </div>
        )
      }
    </div>
  )
}

export default Recto
