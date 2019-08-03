import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'

import Thumb from './Thumb'

const Recto = ({
  areDetailsVisible,
  extraClassName,
  frontText,
  thumbUrl,
  withMediation
}) => (
  <div className={classnames('recto', extraClassName)}>
    {thumbUrl && (
      <Thumb
        src={thumbUrl}
        translated={areDetailsVisible}
        withMediation={withMediation}
      />
    )}
    {frontText && <div className="mediation-front-text fs20">{frontText}</div>}
  </div>
)

Recto.defaultProps = {
  extraClassName: null,
  frontText: null,
  thumbUrl: null,
  withMediation: null
}

Recto.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  extraClassName: PropTypes.string,
  frontText: PropTypes.string,
  thumbUrl: PropTypes.string,
  withMediation: PropTypes.bool
}

export default Recto
