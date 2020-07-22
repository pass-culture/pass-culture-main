import React from 'react'
import PropTypes from 'prop-types'
import Icon from '../../../layout/Icon/Icon'

const BusinessModule = ({ module }) => {
  const { firstLine, image, secondLine, url } = module

  return (
    <div className="business-module-wrapper">
      <a
        href={url}
        rel="noopener noreferrer"
        target="_blank"
      >
        <div className="bmw-image-wrapper">
          <img
            alt=""
            className="bmw-image"
            src={image}
          />
          <div className="bmw-text-wrapper">
            <span>
              {firstLine}
            </span>
            <span>
              {secondLine}
            </span>
          </div>
          <div className="bmw-icon-wrapper">
            <Icon
              className="bmw-next-icon"
              svg="ico-arrow-next"
            />
          </div>
        </div>
      </a>
    </div>
  )
}

BusinessModule.propTypes = {
  module: PropTypes.shape({
    firstLine: PropTypes.string,
    image: PropTypes.string,
    secondLine: PropTypes.string,
    url: PropTypes.string
  }).isRequired
}

export default BusinessModule
