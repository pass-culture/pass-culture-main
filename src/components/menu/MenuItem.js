import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Item from './Item'

const MenuItem = ({ disabled, item }) => {
  const { icon, href, path, target, title } = item
  if (href) {
    return (
      <a
        className="navlink mx12 flex-columns"
        disabled={disabled}
        href={href}
        key={href}
        rel={(target === '_blank' && 'noopener noreferer') || null}
        target={target}
      >
        <Item
          icon={icon}
          title={title}
        />
      </a>
    )
  }
  return (
    <Link
      className="flex-columns mx12 navlink"
      disabled={disabled}
      key={path}
      role="menuitem"
      to={path}
    >
      <Item
        icon={icon}
        title={title}
      />
    </Link>
  )
}

MenuItem.propTypes = {
  disabled: PropTypes.bool.isRequired,
  item: PropTypes.shape({
    disabled: PropTypes.bool,
    href: PropTypes.string,
    icon: PropTypes.string.isRequired,
    path: PropTypes.string.isRequired,
    target: PropTypes.string,
    title: PropTypes.string.isRequired,
  }).isRequired,
}

export default MenuItem
