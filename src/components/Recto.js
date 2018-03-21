import classnames from 'classnames'
import React from 'react'

import Loading from './Loading'

const Recto = ({
  firstThumbDominantColor,
  isFullWidth,
  isLoading,
  thumbUrl,
}) => {
  return isLoading ? (<div className='recto__loading flex items-center justify-center'>
                   <Loading isForceActive />
                 </div>)
              : (<div className={classnames('recto', { 'recto--small': !isFullWidth })} >
                   <div className="card-background" style={{ backgroundImage: `url('${thumbUrl}')`}} />
                   <img draggable="false"
                        src={thumbUrl} />
                   <div className="card-gradient" />
                 </div>)
}

export default Recto
