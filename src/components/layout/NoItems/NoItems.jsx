import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

const NoItems = ({ sentence }) => (
  <div className="teaser-container">
    <Link
      className="teaser-link-offers"
      to="/decouverte"
    >
      {'Lance-toi !'}
    </Link>
    <p className="teaser-text">
      {sentence}
    </p>
  </div>
)

NoItems.propTypes = {
  sentence: PropTypes.string.isRequired,
}

export default NoItems
