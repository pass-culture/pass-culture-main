import React from 'react'

import MediationItem from './MediationItem'

const Recto = ({ id,
  mediation,
  thumbUrl
}) => {
  return (
    <div className='recto' style={{
      backgroundImage: `url(${thumbUrl})`,
      backgroundRepeat: 'no-repeat',
      backgroundSize: 'cover'
    }}>
      <div className='recto__info absolute bottom-0 left-0 right-0 m2 p1 relative'>
        <div className='mb1'>
          {id}
        </div>
        <div className='flex items-center justify-center'>
        {
          mediation && <MediationItem {...mediation} />
        }
        </div>
      </div>
    </div>
  )
}

export default Recto
