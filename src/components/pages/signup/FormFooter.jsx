import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import { NavLink } from 'react-router-dom'

const FormFooter = ({ canSubmit, isLoading }) => (
  <footer>
    <button
      className={classnames("button is-primary is-inverted", {
        'is-loading': isLoading,
      })}
      disabled={!canSubmit}
      type="submit"
    >
      {'Créer'}
    </button>
    <NavLink
      className="button is-secondary"
      to="/connexion"
    >
      {"J'ai déjà un compte"}
    </NavLink>
  </footer>
)

FormFooter.defaultProps = {
  canSubmit: false,
  isLoading: false
}

FormFooter.propTypes = {
  canSubmit: PropTypes.bool,
  isLoading: PropTypes.bool
}

export default FormFooter
