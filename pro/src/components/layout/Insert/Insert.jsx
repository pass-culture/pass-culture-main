import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../Icon'

const Insert = ({ icon, children, className }) => (
  <div className={className}>
    {icon && <Icon png="picto-info-solid-black" />}
    <span>{children}</span>
  </div>
)

Insert.defaultProps = {
  className: 'blue-insert',
  icon: null,
}

Insert.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.node,
  icon: PropTypes.string,
}

export default Insert
