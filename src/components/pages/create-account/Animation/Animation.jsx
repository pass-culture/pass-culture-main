import lottie from 'lottie-web'
import PropTypes from 'prop-types'
import React, { useEffect, useRef } from 'react'

import { ANIMATIONS_URL } from '../../../../utils/config'

export const Animation = ({ name, loop, speed }) => {
  const animationContainer = useRef(null)

  useEffect(() => {
    lottie
      .loadAnimation({
        container: animationContainer.current,
        renderer: 'svg',
        loop: loop,
        autoplay: true,
        path: `${ANIMATIONS_URL}/${name}.json`,
      })
      .setSpeed(speed)
  }, [])

  return (
    <div
      className="animation"
      ref={animationContainer}
    />
  )
}

Animation.defaultProps = {
  loop: false,
  speed: 1,
}

Animation.propTypes = {
  loop: PropTypes.bool,
  name: PropTypes.string.isRequired,
  speed: PropTypes.number,
}
