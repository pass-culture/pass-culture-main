import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

const NoItems = ({ sentence }) => (
  <div className="teaser-container">
    <div className="teaser-link-container">
      <Link
        className="teaser-link-offers"
        to="/"
      >
        {'Lance-toi !'}
      </Link>
    </div>
    <p className="teaser-text">
      {sentence}
    </p>
  </div>
)

NoItems.propTypes = {
  sentence: PropTypes.string.isRequired,
}

export default NoItems
