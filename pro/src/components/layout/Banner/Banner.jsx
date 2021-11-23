/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'
import { requiredIfComponentHasProp } from 'utils/propTypes'

const Banner = ({
  icon,
  href,
  linkTitle,
  children,
  type,
  closable,
  handleOnClick,
  className,
}) => {
  return (
    <div className={`bi-banner ${type} ${className}`}>
      {closable && (
        <button onClick={handleOnClick} type="button">
          x
        </button>
      )}

      <p>{children}</p>

      {href && linkTitle && (
        <p>
          <a
            className="bi-link tertiary-link"
            href={href}
            rel="noopener noreferrer"
            target="_blank"
          >
            <Icon svg={icon} />
            {linkTitle}
          </a>
        </p>
      )}
    </div>
  )
}

Banner.defaultProps = {
  children: null,
  className: '',
  closable: false,
  handleOnClick: null,
  href: null,
  icon: 'ico-external-site',
  linkTitle: null,
  type: 'attention',
}

Banner.propTypes = {
  children: PropTypes.node,
  className: PropTypes.string,
  closable: PropTypes.bool,
  handleOnClick: PropTypes.func,
  href: requiredIfComponentHasProp('linkTitle', 'string'),
  icon: PropTypes.string,
  linkTitle: requiredIfComponentHasProp('href', 'string'),
  type: PropTypes.oneOf(['notification-info', 'attention']),
}

export default Banner
