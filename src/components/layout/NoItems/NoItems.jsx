import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

const NoItems = ({ isHomepageDisabled, sentence }) => (
  <div className="teaser-container">
    <div className="teaser-link-container">
      <Link
        className="teaser-link-offers"
        to={isHomepageDisabled ? "/decouverte" : "/accueil"}
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
  isHomepageDisabled: PropTypes.bool.isRequired,
  sentence: PropTypes.string.isRequired,
}

export default NoItems
