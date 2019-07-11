import PropTypes from 'prop-types'
import React from 'react'
import { NavLink } from 'react-router-dom'

const ModifyOrCancelControl = ({
  isCreatedEntity,
  form,
  history,
  offererId,
  venueId,
  readOnly,
}) => (
  <div className="control">
    {readOnly ? (
      <NavLink
        className="button is-secondary is-medium"
        id="modify-venue"
        to={`/structures/${offererId}/lieux/${venueId}?modification`}
      >
        Modifier le lieu
      </NavLink>
    ) : (
      <button
        className="button is-secondary is-medium"
        onClick={() => {
          form.reset()
          const next = isCreatedEntity
            ? `/structures/${offererId}`
            : `/structures/${offererId}/lieux/${venueId}`
          history.push(next)
        }}
        type="reset"
      >
        Annuler
      </button>
    )}
  </div>
)

ModifyOrCancelControl.defaultProps = {
  venueId: null,
}

ModifyOrCancelControl.propTypes = {
  form: PropTypes.object.isRequired,
  history: PropTypes.object.isRequired,
  isCreatedEntity: PropTypes.bool.isRequired,
  offererId: PropTypes.string.isRequired,
  readOnly: PropTypes.bool.isRequired,
  venueId: PropTypes.string,
}

export default ModifyOrCancelControl
