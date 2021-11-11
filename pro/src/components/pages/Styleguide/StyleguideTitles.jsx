/*
* @debt directory "Gaël: this file should be migrated within storybook"
*/

import PropTypes from 'prop-types'
import React from 'react'

const StyleguideTitle = ({ className, componentName }) => {
  return (
    <div>
      <hr className="separator" />
      <h2 id={className}>
        {componentName}
      </h2>
    </div>
  )
}

StyleguideTitle.propTypes = {
  className: PropTypes.string.isRequired,
  componentName: PropTypes.string.isRequired,
}

export default StyleguideTitle
