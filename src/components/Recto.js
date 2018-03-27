import classnames from 'classnames'
import React from 'react'
import { connect } from 'react-redux'

import RectoDebug from './RectoDebug'
import Loading from './Loading'
import { IS_DEV } from '../utils/config'
import selectThumbUrl from '../selectors/thumbUrl'


const Recto = props => {
  const {
    id,
    isLoading,
    thumbUrl,
  } = props
  const style = isLoading
    ? { backgroundColor: 'black' }
    : { backgroundImage: `url('${thumbUrl}')`}
  return (
    <div className='recto'>
       <div className={classnames('card-background', {
           'card-background--loading flex items-center justify-center': isLoading
         })} style={style}>
        {isLoading && <Loading isForceActive />}
      </div>
      { id && (
        <div>
          <img alt='thumb'
            src={thumbUrl} />
          {IS_DEV && <RectoDebug {...props} />}
        </div>
      )}
     </div>
  )
}

export default connect(
  (state, ownProps) => ({
    isFlipped: state.navigation.isFlipped,
    thumbUrl: selectThumbUrl(state, ownProps)
  }))(Recto)
