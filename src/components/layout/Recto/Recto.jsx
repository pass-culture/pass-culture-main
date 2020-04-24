import PropTypes from 'prop-types'
import React from 'react'

import Thumb from './Thumb'

const Recto = ({ areDetailsVisible, thumbUrl, withMediation }) => (
  <div className="recto">
    {thumbUrl && (
      <Thumb
        src={thumbUrl}
        translated={areDetailsVisible}
        withMediation={withMediation}
      />
    )}
  </div>
)

Recto.defaultProps = {
  thumbUrl: null,
  withMediation: null,
}

Recto.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  thumbUrl: PropTypes.string,
  withMediation: PropTypes.bool,
}

export default Recto
