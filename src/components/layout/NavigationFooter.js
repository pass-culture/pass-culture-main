import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { toggleMainMenu } from '../../reducers/menu'

const NavigationFooter = ({ className, dispatch, theme }) => {
  const cssclass = `pc-theme-${theme} pc-footer flex-center flex-0 ${className}`
  return (
    <footer className={cssclass}>
      <button
        type="button"
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
}

NavigationFooter.propTypes = {
  className: PropTypes.string,
  dispatch: PropTypes.func.isRequired,
  theme: PropTypes.string.isRequired,
}

export default connect()(NavigationFooter)
