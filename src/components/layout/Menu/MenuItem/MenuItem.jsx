import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'
import Item from './Item/Item'

const MenuItem = ({ isDisabled, item }) => {
  const { icon, href, path, target, title } = item

  if (href) {
    return (
      <a
        className="navlink mx12 flex-columns"
        disabled={isDisabled}
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
      disabled={isDisabled}
      key={path}
      role="menuitem"
      to={isDisabled ? '#' : path}
    >
      <Item
        icon={icon}
        title={title}
      />
    </Link>
  )
}

MenuItem.defaultProps = {
  isDisabled: false,
}

MenuItem.propTypes = {
  isDisabled: PropTypes.bool,
  item: PropTypes.shape({
    href: PropTypes.string,
    icon: PropTypes.string.isRequired,
    path: PropTypes.string,
    target: PropTypes.string,
    title: PropTypes.string.isRequired,
  }).isRequired,
}

export default MenuItem
