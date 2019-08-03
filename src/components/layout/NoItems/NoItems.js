import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import { Link } from 'react-router-dom'

const NoItems = ({ withWhiteBackground, sentence }) => (
  <Fragment>
    <Link
      className={classnames("teaser-link-offers", { red: withWhiteBackground })}
      to="/decouverte"
    >
      {'Lancez-vous'}
    </Link>
    <p className={classnames("teaser-text", { red: withWhiteBackground })}>
      {sentence}
      <br />
      {'vous la retrouverez ici.'}
    </p>
  </Fragment>
)

NoItems.defaultProps = {
  withWhiteBackground: false
}

NoItems.propTypes = {
  sentence: PropTypes.string.isRequired,
  withWhiteBackground: PropTypes.bool
}

export default NoItems
