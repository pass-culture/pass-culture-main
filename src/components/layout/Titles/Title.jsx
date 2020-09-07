import PropTypes from 'prop-types'
import React from 'react'

const Title = ({ title }) => (
  <h1>
    {title}
  </h1>
)


Title.propTypes = {
  title: PropTypes.string.isRequired,
}

export default Title
