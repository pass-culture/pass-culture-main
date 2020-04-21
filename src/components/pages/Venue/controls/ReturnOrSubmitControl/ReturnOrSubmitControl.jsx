import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import { NavLink } from 'react-router-dom'

const ReturnOrSubmitControl = ({
  canSubmit,
  isCreatedEntity,
  isRequestPending,
  offererId,
  readOnly,
}) => (
  <div className="control">
    <div
      className="field is-grouped is-grouped-centered"
      style={{ justifyContent: 'space-between' }}
    >
      <div className="control">
        {readOnly ? (
          <NavLink className="button is-primary is-medium" to={`/structures/${offererId}`}>
            {'Terminer'}
          </NavLink>
        ) : (
          <button
            className={classnames('button is-primary is-medium', {
              'is-loading': isRequestPending,
            })}
            disabled={!canSubmit}
            type="submit"
          >
            {isCreatedEntity ? 'Créer' : 'Valider'}
          </button>
        )}
      </div>
    </div>
  </div>
)

ReturnOrSubmitControl.defaultProps = {
  isCreatedEntity: false,
  isRequestPending: false,
  offererId: null,
  readOnly: true,
}

ReturnOrSubmitControl.propTypes = {
  canSubmit: PropTypes.bool.isRequired,
  isCreatedEntity: PropTypes.bool,
  isRequestPending: PropTypes.bool,
  offererId: PropTypes.string,
  readOnly: PropTypes.bool,
}

export default ReturnOrSubmitControl
