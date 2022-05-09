import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'

import Icon from './Icon'

const Spinner = ({ message }) => {
  const [nbDots, setNbDots] = useState(3)
  const [timer, setTimer] = useState(null)

  useEffect(() => {
    if (timer) window.clearInterval(timer)
    const newTimer = window.setInterval(() => {
      setNbDots(oldVal => (oldVal % 3) + 1)
    }, 500)
    setTimer(newTimer)
    return () => {
      window.clearInterval(newTimer)
    }
  }, [])

  return (
    <div className="loading-spinner" data-testid="spinner">
      <Icon svg="loader-pc" />
      <div className="content" data-dots={Array(nbDots).fill('.').join('')}>
        {message}
      </div>
    </div>
  )
}

Spinner.defaultProps = {
  message: 'Chargement en cours',
}

Spinner.propTypes = {
  message: PropTypes.string,
}

export default Spinner
