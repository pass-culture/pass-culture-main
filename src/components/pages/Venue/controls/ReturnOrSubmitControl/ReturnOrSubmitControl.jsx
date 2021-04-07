import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

const ReturnOrSubmitControl = ({
  canSubmit,
  isCreatedEntity,
  isNewHomepageActive,
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
          <Link
            className="primary-link"
            to={
              isNewHomepageActive ? `/accueil?structure=${offererId}` : `/structures/${offererId}`
            }
          >
            {'Terminer'}
          </Link>
        ) : (
          <button
            className={classnames('primary-button', {
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
  isNewHomepageActive: false,
  isRequestPending: false,
  offererId: null,
  readOnly: true,
}

ReturnOrSubmitControl.propTypes = {
  canSubmit: PropTypes.bool.isRequired,
  isCreatedEntity: PropTypes.bool,
  isNewHomepageActive: PropTypes.bool,
  isRequestPending: PropTypes.bool,
  offererId: PropTypes.string,
  readOnly: PropTypes.bool,
}

export default ReturnOrSubmitControl
