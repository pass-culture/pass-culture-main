import React from 'react'
import PropTypes from 'prop-types'

const BusinessModule = ({ module, titleClassName }) => {
  const { image, title, url } = module
  return (
    <div>
      <img
        alt=""
        src={image}
      />
      <h1 className={titleClassName}>
        {title}
      </h1>
      <span>
        {url}
      </span>
    </div>
  )
}

BusinessModule.propTypes = {
  module: PropTypes.shape({
    image: PropTypes.string,
    title: PropTypes.string,
    url: PropTypes.string
  }).isRequired,
  titleClassName: PropTypes.string.isRequired
}

export default BusinessModule
