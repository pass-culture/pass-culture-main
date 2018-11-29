/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

const ErrorCatcherView = ({ onClick }) => (
  <div id="error-catcher">
    <div className="flex-1 flex-rows flex-center">
      <h2 className="fs20">Une erreur est survenue.</h2>
      <p className="mt12">
        <button
          type="button"
          onClick={onClick}
          className="no-background border-all rd4 py12 px18 is-inline-block is-white-text text-center fs16"
        >
          <span>Retour aux offres</span>
        </button>
      </p>
    </div>
  </div>
)

ErrorCatcherView.propTypes = {
  onClick: PropTypes.func.isRequired,
}

export default ErrorCatcherView
