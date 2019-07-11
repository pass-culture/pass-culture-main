import PropTypes from 'prop-types'
import classnames from 'classnames'
import React from 'react'

const Thumb = ({ withMediation, src, translated }) => {
  const backgroundStyle = (src && { backgroundImage: `url('${src}')` }) || {}
  const thumbStyle = Object.assign(backgroundStyle, {
    backgroundSize: withMediation ? 'cover' : null,
  })
  return (
    <div className="thumb">
      {!withMediation && <div
        className="background"
        style={backgroundStyle}
                         />}
      <div
        className={classnames({
          image: true,
          translatable: translated !== undefined,
          translated,
        })}
        style={thumbStyle}
      />
    </div>
  )
}

Thumb.defaultProps = {
  src: null,
  translated: false,
  withMediation: null,
}

Thumb.propTypes = {
  src: PropTypes.string,
  translated: PropTypes.bool,
  withMediation: PropTypes.object,
}

export default Thumb
