/* eslint
  react/jsx-one-expression-per-line: 0 */
import React, { Fragment } from 'react'
import PropTypes from 'prop-types'

const BookingFooter = ({
  onCancel,
  onSubmit,
  isBooked,
  isSubmitting,
  canSubmitForm,
}) => {
  const showOkButton = isBooked
  const showCancelButton = !isSubmitting && !isBooked
  const showSubmitButton = showCancelButton && canSubmitForm
  return (
    <Fragment>
      {showCancelButton && (
        <button type="reset" onClick={onCancel} className="text-center my5">
          <span>Annuler</span>
        </button>
      )}
      {showSubmitButton && (
        <button type="submit" onClick={onSubmit} className="text-center my5">
          <b>Valider</b>
        </button>
      )}
      {showOkButton && (
        <button type="button" onClick={onCancel} className="text-center my5">
          <b>OK</b>
        </button>
      )}
    </Fragment>
  )
}

BookingFooter.defaultProps = {}

BookingFooter.propTypes = {
  canSubmitForm: PropTypes.bool.isRequired,
  isBooked: PropTypes.bool.isRequired,
  isSubmitting: PropTypes.bool.isRequired,
  onCancel: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
}

export default BookingFooter
