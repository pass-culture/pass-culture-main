import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { toggleMainMenu } from '../../reducers/menu'

const NavigationFooter = ({ dispatch, className }) => {
  const cssclass = `pc-footer dotted-top flex-columns flex-center items-center flex-0 ${className}`
  return (
    <footer className={cssclass}>
      <button
        type="button"
        onClick={() => dispatch(toggleMainMenu())}
        className="no-border no-background is-white"
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
}

export default connect()(NavigationFooter)
