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

export default Thumb
