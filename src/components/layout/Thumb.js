import classnames from 'classnames'
import React from 'react'

const Thumb = ({ src, translated }) => {
  const backgroundStyle = { backgroundImage: `url('${src}')` }
  const thumbStyle = Object.assign(backgroundStyle, {
    backgroundSize: 'cover'
  })
  return (
    <div className="thumb">
      <div className="background" 
        style={backgroundStyle} />
    </div>
  )
}

export default Thumb
