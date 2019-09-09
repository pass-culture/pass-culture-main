import PropTypes from 'prop-types'
import React from 'react'

const Label = ({ title }) => (
  <div className="subtitle can-be-required">
    {title}
  </div>
)

Label.propTypes = {
  title: PropTypes.string.isRequired,
}

export default Label
