import PropTypes from 'prop-types'
import React from 'react'

export const VenueName = ({ name }) => (
  <div className="field field-select is-horizontal readonly">
    <div className="field-label readonly">
      {'Lieu :'}
    </div>
    <div className="field-body field-content">
      {name}
    </div>
  </div>
)

VenueName.propTypes = {
  name: PropTypes.string.isRequired,
}
