import PropTypes from 'prop-types'
import React from 'react'

import Item from './Item'

const SimpleLink = ({ item }) => (
  <a
    className="navlink mx12 flex-columns"
    disabled={item.disabledInMenu}
    href={item.href}
    key={item.href}
    rel={(item.target === '_blank' && 'noopener noreferer') || null}
    target={item.target}
  >
    <Item
      icon={item.icon}
      title={item.title}
    />
  </a>
)

SimpleLink.propTypes = {
  item: PropTypes.shape({
    disabled: PropTypes.bool,
    href: PropTypes.string.isRequired,
    icon: PropTypes.string.isRequired,
    target: PropTypes.string,
    title: PropTypes.string.isRequired,
  }).isRequired,
}

export default SimpleLink
