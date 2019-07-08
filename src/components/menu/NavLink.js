import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Item from './Item'

const NavLink = ({ item }) => (
  <Link
    className="flex-columns mx12 navlink"
    disabled={item.disabled}
    key={item.path}
    role="menuitem"
    to={item.path}
  >
    <Item
      icon={item.icon}
      title={item.title}
    />
  </Link>
)

NavLink.propTypes = {
  item: PropTypes.shape({
    disabled: PropTypes.bool,
    icon: PropTypes.string.isRequired,
    path: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
  }).isRequired,
}

export default NavLink
