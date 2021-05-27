import React from 'react'
import trackGeolocation from './trackGeolocation'

export default WrappedComponent => {
  // eslint-disable-next-line react/function-component-definition
  return function withGeolocationTracking(props) {
    return (
      <WrappedComponent
        trackGeolocation={trackGeolocation}
        {...props}
      />
    )
  }
}
