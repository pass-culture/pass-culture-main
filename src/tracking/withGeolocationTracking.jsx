import React from 'react'
import trackGeolocation from './trackGeolocation'

export default WrappedComponent => {
  return function withGeolocationTracking(props) {
    return (<WrappedComponent
      trackGeolocation={trackGeolocation}
      {...props}
            />)
  }
}
