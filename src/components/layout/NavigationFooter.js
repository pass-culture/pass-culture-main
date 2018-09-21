import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { toggleMainMenu } from '../../reducers/menu'

const NavigationFooter = ({ className, disabled, dispatch, theme }) => {
  const cssclass = `pc-theme-${theme} pc-footer flex-center flex-none ${className}`
  return (
    <footer className={cssclass}>
      <button
        type="button"
        disabled={disabled}
        id="open-menu-button"
        onClick={() => dispatch(toggleMainMenu())}
        className="no-border no-background no-outline no-select"
      >
        <span
          aria-hidden
          className="icon-user-circle-outline"
          title="Afficher le menu de navigation"
        />
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
  dispatch: PropTypes.func.isRequired,
  theme: PropTypes.string.isRequired,
}

export default connect()(NavigationFooter)
