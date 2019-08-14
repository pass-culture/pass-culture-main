import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

import Icon from '../../../Icon'

const Item = ({ icon, title }) => (
  <Fragment>
    <span className="flex-0 text-center menu-icon mr16">
      <Icon
        alt=""
        svg={`ico-${icon}`}
      />
    </span>
    <span className="flex-1 is-medium">{title}</span>
  </Fragment>
)

Item.propTypes = {
  icon: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
}

export default Item
