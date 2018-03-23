import React from 'react'

import RectoDebug from './RectoDebug'
import Loading from './Loading'
import { IS_DEV } from '../utils/config'

const Recto = props => {
  const { isLoading,
    thumbUrl,
  } = props
  return isLoading
    ? (
      <div className='recto__loading flex items-center justify-center'>
        <Loading isForceActive />
      </div>
    )
    : (
      <div className='recto'>
         <div className="card-background" style={{ backgroundImage: `url('${thumbUrl}')`}} />
         <img draggable="false"
              src={thumbUrl}
              alt='thumb' />
         { IS_DEV && <RectoDebug {...props} /> }
       </div>
    )
}

export default Recto
