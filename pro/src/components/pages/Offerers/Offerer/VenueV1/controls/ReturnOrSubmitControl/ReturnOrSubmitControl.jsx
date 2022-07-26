import { Events } from 'core/FirebaseEvents/constants'
import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'
import React from 'react'
import classnames from 'classnames'
import { useSelector } from 'react-redux'

const ReturnOrSubmitControl = ({
  canSubmit,
  isCreatedEntity,
  isNewBankInformationCreation,
  isRequestPending,
  offererId,
  readOnly,
}) => {
  const logEvent = useSelector(state => state.app.logEvent)
  return (
    <div className="control">
      <div
        className="field is-grouped is-grouped-centered"
        style={{ justifyContent: 'space-between' }}
      >
        <div className="control">
          {readOnly ? (
            <Link
              className="primary-link"
              to={`/accueil?structure=${offererId}`}
            >
              Terminer
            </Link>
          ) : (
            <button
              className={classnames('primary-button', {
                'is-loading': isRequestPending,
              })}
              disabled={!canSubmit || isRequestPending}
              type="submit"
              onClick={() => {
                logEvent(Events.CLICKED_SAVE_VENUE, {
                  from: location.pathname,
                })
              }}
            >
              {isCreatedEntity
                ? isNewBankInformationCreation
                  ? 'Enregistrer et continuer'
                  : 'Créer'
                : 'Valider'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

ReturnOrSubmitControl.defaultProps = {
  isCreatedEntity: false,
  isNewBankInformationCreation: false,
  isRequestPending: false,
  offererId: null,
  readOnly: true,
}

ReturnOrSubmitControl.propTypes = {
  canSubmit: PropTypes.bool.isRequired,
  isCreatedEntity: PropTypes.bool,
  isNewBankInformationCreation: PropTypes.bool,
  isRequestPending: PropTypes.bool,
  offererId: PropTypes.string,
  readOnly: PropTypes.bool,
}

export default ReturnOrSubmitControl
