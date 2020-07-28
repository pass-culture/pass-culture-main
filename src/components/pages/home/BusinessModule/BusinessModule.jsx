import React from 'react'
import PropTypes from 'prop-types'
import Icon from '../../../layout/Icon/Icon'
import BusinessPane from '../domain/ValueObjects/BusinessPane'

const BusinessModule = ({ module }) => {
  const { firstLine, image, secondLine, url } = module

  return image && (
    <section className="business-module-wrapper">
      <a
        className="bmw-image-wrapper"
        href={url}
        rel="noopener noreferrer"
        target="_blank"
      >
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
            svg="ico-arrow-next"
          />
        </div>
      </a>
    </section>
  )
}

BusinessModule.propTypes = {
  module: PropTypes.instanceOf(BusinessPane).isRequired
}

export default BusinessModule
