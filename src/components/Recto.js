import classnames from 'classnames'
import React from 'react'

import Debug from './Debug'
import Loading from './Loading'
import { IS_DEV } from '../utils/config'

const Recto = props => {
  const {
    isFullWidth,
    isLoading,
    thumbUrl,
  } = props
  return isLoading
    ? (
      <div className='recto__loading flex items-center justify-center'>
        <Loading isForceActive />
      </div>
    )
    : (
      <div className={classnames('recto', { 'recto--small': !isFullWidth })} >
         <div className="card-background" style={{ backgroundImage: `url('${thumbUrl}')`}} />
         <img draggable="false"
              src={thumbUrl}
              alt='thumb' />
         { IS_DEV && <Debug {...props} /> }
       </div>
    )
}

export default Recto
