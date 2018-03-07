import React from 'react'

import Loading from './Loading'
import MediationItem from './MediationItem'

const Recto = ({ contentLength,
  id,
  index,
  isLoading,
  item,
  mediation,
  thumbUrl
}) => {
  return (
    <div className='recto' style={{
      backgroundImage: `url(${thumbUrl})`,
      backgroundRepeat: 'no-repeat',
      backgroundSize: 'cover'
    }}>
      {
        isLoading
          ? (
            <div className='recto__loading flex items-center justify-center'>
              <Loading isForceActive />
            </div>
          )
          : (
            <div className='recto__info absolute bottom-0 left-0 right-0 m2 p1 relative'>
              <div className='mb1'>
                {id} {index}/{contentLength} {item}
              </div>
              <div className='flex items-center justify-center'>
              {
                mediation && <MediationItem {...mediation} />
              }
              </div>
            </div>
          )
      }
    </div>
  )
}

export default Recto
