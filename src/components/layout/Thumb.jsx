import PropTypes from 'prop-types'
import React from 'react'

const Thumb = ({ src }) => {
  const backgroundStyle = { backgroundImage: `url('${src}')` }
  return (
    <div className="thumb">
      <div
        className="background"
        style={backgroundStyle}
      />
    </div>
  )
}

Thumb.propTypes = {
  src: PropTypes.string.isRequired,
}

export default Thumb
