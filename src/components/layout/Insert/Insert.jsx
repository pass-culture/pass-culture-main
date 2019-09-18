import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../Icon'

const Insert = ({ children }) => (
  <div className="insert">
    <Icon png="picto-info-solid-black" />
    <span>
      {children}
    </span>
  </div>
)

Insert.propTypes = {
  children: PropTypes.node.isRequired,
}

export default Insert
