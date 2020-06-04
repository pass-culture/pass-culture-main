import PropTypes from 'prop-types'
import React, { forwardRef } from 'react'

import Icon from '../../../layout/Icon/Icon'

const Header = forwardRef(function Header(props, ref) {
  return (
    <form
      action=""
      className="sh-form"
      id="home-form"
      onSubmit={props.onSubmit}
    >
      <div className="sh-input-wrapper">
        <div className="sh-input-left">
          {props.onBackButtonClick ? (
            <button
              className="sr-input-back"
              onClick={props.onBackButtonClick}
              type="button"
            >
              <Icon
                alt="Réinitialiser la recherche"
                svg="picto-back-grey"
              />
            </button>
          ) : (
            <Icon svg="picto-search" />
          )}
        </div>
        <input
          className="sh-text-input"
          name="keywords"
          onChange={props.onSearchChange}
          placeholder="Titre, artiste..."
          ref={ref}
          type="search"
          value={props.value}
        />
        <div className="sh-reset-wrapper">
          {props.value && (
            <button
              className="sh-reset-button"
              onClick={props.onResetClick}
              type="reset"
            >
              <Icon
                alt="Supprimer la saisie"
                svg="picto-reset"
              />
            </button>
          )}
        </div>
      </div>
    </form>
  )
})

Header.defaultProps = {
  onBackButtonClick: null,
  value: '',
}

Header.propTypes = {
  onBackButtonClick: PropTypes.func,
  onResetClick: PropTypes.func.isRequired,
  onSearchChange: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  value: PropTypes.string,
}

export default Header
