import PropTypes from 'prop-types'
import React from 'react'

import Thumb from './Thumb'

const Recto = ({ areDetailsVisible, thumbUrl }) => (
  <div className="recto">
    {thumbUrl && (
      <Thumb
        src={thumbUrl}
        translated={areDetailsVisible}
      />
    )}
  </div>
)

Recto.defaultProps = {
  thumbUrl: null,
}

Recto.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  thumbUrl: PropTypes.string,
}

export default Recto
