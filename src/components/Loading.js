import React from 'react'
import { connect } from 'react-redux'

const Loading = ({ className,
  isForceActive,
  isActive
}) => {
  return (
    <div className={className || 'loading'}>
      {
        (isActive || isForceActive) && <div className='loading__container' />
      }
    </div>
  )
}

export default connect((state, ownProps) => ({
    isActive: state.loading.isActive && ownProps.tag === state.loading.tag
  }))(Loading)
