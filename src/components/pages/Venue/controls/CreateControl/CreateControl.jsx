import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

const CreateControl = ({ venueId, offererId }) => (
  <div className="control">
    <div
      className="field is-grouped is-grouped-centered"
      style={{ justifyContent: 'space-between' }}
    >
      <div className="control">
        <Link
          className="button is-tertiary is-medium"
          to={`/offres/creation?lieu=${venueId}&structure=${offererId}`}
        >
          <span>
            {'Créer une offre dans ce lieu'}
          </span>
        </Link>
      </div>
    </div>
  </div>
)

CreateControl.propTypes = {
  venueId: PropTypes.string.isRequired,
}

export default CreateControl
