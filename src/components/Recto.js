import classnames from 'classnames'
import React from 'react'

import RectoDebug from './RectoDebug'
import Loading from './Loading'
import { IS_DEV } from '../utils/config'

const Recto = props => {
  const { isLoading, thumbUrl } = props
  const style = isLoading
    ? { backgroundColor: 'black' }
    : { backgroundImage: `url('${thumbUrl}')`}
  return (
    <div className='recto'>
       <div className={classnames('card-background', {
         'card-background--loading flex items-center justify-center': isLoading
       })}
        style={style}>
         {isLoading && <Loading isForceActive />}
        </div>
        {
          !isLoading && [
             <img alt='thumb'
                draggable="false"
                key={0}
                src={thumbUrl} />,
             IS_DEV && <RectoDebug key={1} {...props} />
           ]
        }
     </div>
  )
}

export default Recto
