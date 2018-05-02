import classnames from 'classnames'
import React from 'react'

const Thumb = ({ withMediation, src, translated }) => {
  const backgroundStyle = { backgroundImage: `url('${src}')` }
  const thumbStyle = Object.assign(backgroundStyle, {
    backgroundSize: withMediation ? 'cover' : null,
  })
  return (
    <div className="thumb">
      {!withMediation && <div className="background" style={backgroundStyle} />}
      <div
        style={thumbStyle}
        className={classnames({
          image: true,
          translatable: translated !== undefined,
          translated,
        })}
      />
    </div>
  )
}

export default Thumb
