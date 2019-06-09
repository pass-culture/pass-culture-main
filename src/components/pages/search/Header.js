import PropTypes from 'prop-types'
import React from 'react'

export const Header = ({ title }) => (
  <header className="no-dotted-border">
    <h1 className="is-normal fs19">
      {title}
    </h1>
  </header>
)

Header.propTypes = {
  title: PropTypes.string.isRequired,
}
