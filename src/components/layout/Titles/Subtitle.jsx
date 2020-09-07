import PropTypes from 'prop-types'
import React from 'react'

const Subtitle = ({ subtitle }) => (
  <h2>
    {subtitle}
  </h2>
)

Subtitle.propTypes = {
  subtitle: PropTypes.string.isRequired,
}

export default Subtitle
