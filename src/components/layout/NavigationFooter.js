import React from 'react'
import PropTypes from 'prop-types'
import { Link, withRouter } from 'react-router-dom'

const NavigationFooter = ({ className, disabled, location, theme }) => {
  const cssclass = `pc-theme-${theme} pc-footer flex-center flex-none ${className}`
  const cleanPath = location.pathname.replace(/\/$/, '')
  const menuUrl = `${cleanPath}/menu${location.search}`
  return (
    <footer className={cssclass}>
      <Link
        className={`no-border no-background no-outline no-select pc-theme-${theme}`}
        disabled={disabled}
        id="open-menu-button"
        to={menuUrl}
      >
        <span
          aria-hidden
          className="icon-legacy-user-circle-outline"
          title="Afficher le menu de navigation"
        />
      </Link>
    </footer>
  )
}

NavigationFooter.defaultProps = {
  className: '',
  disabled: false,
}

NavigationFooter.propTypes = {
  className: PropTypes.string,
  disabled: PropTypes.bool,
  location: PropTypes.object.isRequired,
  theme: PropTypes.string.isRequired,
}

export default withRouter(NavigationFooter)
