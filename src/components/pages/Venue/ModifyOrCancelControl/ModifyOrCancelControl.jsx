import PropTypes from 'prop-types'
import React from 'react'
import { NavLink } from 'react-router-dom'

const ModifyOrCancelControl = ({
  isCreatedEntity,
  offererId,
  query,
  venueId,
  readOnly,
}) => {
  return (
    <div className="control">
      {readOnly ? (
        <NavLink
          className="button is-secondary is-medium"
          to={`/structures/${offererId}/lieux/${venueId}?modification`}>
          Modifier le lieu
        </NavLink>
      ) : (
        <NavLink
          className="button is-secondary is-medium"
          to={
            isCreatedEntity
              ? `/structures/${offererId}`
              : `/structures/${offererId}/lieux/${venueId}`
          }>
          Annuler
        </NavLink>
      )}
    </div>
  )
}

ModifyOrCancelControl.defaultProps = {
  venueId: null,
}

ModifyOrCancelControl.propTypes = {
  isCreatedEntity: PropTypes.bool.isRequired,
  offererId: PropTypes.string.isRequired,
  venueId: PropTypes.string,
  readOnly: PropTypes.bool.isRequired,
}

export default ModifyOrCancelControl
