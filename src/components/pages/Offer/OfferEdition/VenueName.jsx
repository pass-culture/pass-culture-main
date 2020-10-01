import React from 'react'
import PropTypes from 'prop-types'

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
