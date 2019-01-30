import React from 'react'
import PropTypes from 'prop-types'
import { Link, withRouter } from 'react-router-dom'

const NavigationFooter = ({ className, disabled, location, theme }) => {
  const cssclass = `pc-theme-${theme} pc-footer flex-center flex-none ${className}`
  return (
    <footer className={cssclass}>
      <button
        type="button"
        disabled={disabled}
        id="open-menu-button"
        className="no-border no-background no-outline no-select"
      >
        <Link to={`${location.pathname}/menu${location.search}`}>
          <span
            aria-hidden
            className="icon-legacy-user-circle-outline"
            title="Afficher le menu de navigation"
          />
        </Link>
      </button>
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
