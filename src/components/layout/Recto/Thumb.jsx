import PropTypes from 'prop-types'
import React from 'react'

const Thumb = ({ withMediation, src, translated }) => {
  const backgroundStyle = (src && { backgroundImage: `url('${src}')` }) || {}
  const thumbStyle = Object.assign(backgroundStyle, {
    backgroundSize: withMediation ? 'cover' : null,
    backgroundColor: 'grey',
  })
  return (
    <div className="thumb">
      {!withMediation && <div
        className="background"
        style={backgroundStyle}
                         />}
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
  withMediation: false,
}

Thumb.propTypes = {
  src: PropTypes.string,
  translated: PropTypes.bool,
  withMediation: PropTypes.bool,
}

export default Thumb
