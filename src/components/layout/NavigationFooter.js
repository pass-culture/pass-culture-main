import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { toggleMainMenu } from '../../reducers/menu'

const NavigationFooter = ({ dispatch, className, theme }) => {
  console.log('theme', theme)
  const cssclass = `pc-footer dotted-top flex-center flex-0 ${className}`
  return (
    <footer className={cssclass}>
      <button
        type="button"
        onClick={() => dispatch(toggleMainMenu())}
        className="no-border no-background no-outline no-select is-white"
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
  theme: 'red',
}

NavigationFooter.propTypes = {
  className: PropTypes.string,
  dispatch: PropTypes.func.isRequired,
  theme: PropTypes.string,
}

export default connect()(NavigationFooter)
