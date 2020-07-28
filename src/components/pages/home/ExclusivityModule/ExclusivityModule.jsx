import React from 'react'
import PropTypes from 'prop-types'
import ExclusivityPane from '../domain/ValueObjects/ExclusivityPane'
import { Link } from 'react-router-dom'

const ExclusivityModule = ({ module }) => {
  const { alt, image, offerId } = module

  return image && (
    <section className="exclusivity-module-wrapper">
      <Link
        className="emw-image-wrapper"
        to={`/accueil/details/${offerId}`}
      >
        <img
          alt={alt}
          className="emw-image"
          src={image}
        />
      </Link>
    </section>
  )
}

ExclusivityModule.propTypes = {
  module: PropTypes.instanceOf(ExclusivityPane).isRequired
}

export default ExclusivityModule
