import PropTypes from 'prop-types'
import React from 'react'

const Thumb = ({ src, translated }) => {
  const backgroundStyle = (src && { backgroundImage: `url('${src}')` }) || {}
  const thumbStyle = Object.assign(backgroundStyle, {
    backgroundSize: 'cover',
    backgroundColor: 'grey',
  })
  return (
    <div className="thumb">
      <div
        className={`image ${translated !== undefined ? 'translatable' : ''} ${
          translated ? 'translated' : ''
        }`}
        style={thumbStyle}
      />
    </div>
  )
}

Thumb.defaultProps = {
  src: null,
  translated: false,
}

Thumb.propTypes = {
  src: PropTypes.string,
  translated: PropTypes.bool,
}

export default Thumb
