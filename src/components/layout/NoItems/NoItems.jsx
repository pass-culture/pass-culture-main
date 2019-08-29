import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import { Link } from 'react-router-dom'

const NoItems = ({ sentence }) => (
  <Fragment>
    <Link
      className="teaser-link-offers"
      to="/decouverte"
    >
      {'Lancez-vous'}
    </Link>
    <p className="teaser-text">
      {sentence}
      <br />
      {'vous la retrouverez ici.'}
    </p>
  </Fragment>
)

NoItems.propTypes = {
  sentence: PropTypes.string.isRequired,
}

export default NoItems
