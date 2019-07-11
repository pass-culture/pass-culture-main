import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'

import Thumb from '../layout/Thumb'
import { IS_DEV } from '../../utils/config'

const Recto = ({ areDetailsVisible, extraClassName, recommendation }) => {
  const { dateRead, mediation, id, index, isClicked, offer, thumbUrl } =
    recommendation || {}

  return (
    <div className={classnames('recto', extraClassName)}>
      {thumbUrl && (
        <Thumb
          src={thumbUrl}
          translated={areDetailsVisible}
          withMediation={mediation}
        />
      )}
      {mediation && mediation.frontText && (
        <div className="mediation-front-text fs20">{mediation.frontText}</div>
      )}
      {IS_DEV && (
        <div className="debug debug-recto">
          <div>
            {id} 
            {' '}
            {offer && offer.id} 
            {' '}
            {index}
          </div>
          {dateRead && <div> déjà lue </div>}
          {isClicked && <div> déjà retournée </div>}
        </div>
      )}
    </div>
  )
}

Recto.defaultProps = {
  extraClassName: null,
  recommendation: null,
}

Recto.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  extraClassName: PropTypes.string,
  recommendation: PropTypes.object,
}

export default Recto
