import PropTypes from 'prop-types'
import React from 'react'
import { NavLink } from 'react-router-dom'

const CreateControl = ({ venueId }) => (
  <div className="control">
    <div
      className="field is-grouped is-grouped-centered"
      style={{ justifyContent: 'space-between' }}
    >
      <div className="control">
        <NavLink
          className="button is-secondary is-medium"
          to={`/offres/creation?lieu=${venueId}`}
        >
          <span>
            {'Créer une offre dans ce lieu'}
          </span>
        </NavLink>
      </div>
    </div>
  </div>
)

CreateControl.propTypes = {
  venueId: PropTypes.number.isRequired,
}

export default CreateControl
