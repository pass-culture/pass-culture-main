import React from 'react'

const Thumb = ({ src, translated }) => {
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
