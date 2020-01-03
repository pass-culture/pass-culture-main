import PropTypes from 'prop-types'
import React from 'react'

import Thumb from './Thumb'

const Recto = ({ areDetailsVisible, frontText, thumbUrl, withMediation }) => (
  <div className="recto">
    {thumbUrl && (
      <Thumb
        src={thumbUrl}
        translated={areDetailsVisible}
        withMediation={withMediation}
      />
    )}
    {frontText && <div className="mediation-front-text fs20">
      {frontText}
    </div>}
  </div>
)

Recto.defaultProps = {
  frontText: null,
  thumbUrl: null,
  withMediation: null,
}

Recto.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  frontText: PropTypes.string,
  thumbUrl: PropTypes.string,
  withMediation: PropTypes.bool,
}

export default Recto
