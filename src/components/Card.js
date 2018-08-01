import PropTypes from 'prop-types'
import get from 'lodash.get'
import { requestData } from 'pass-culture-shared'
import React from 'react'
import { connect } from 'react-redux'
import withSizes from 'react-sizes'
import { compose } from 'redux'

import Recto from './Recto'
import Verso from './Verso'

class Card extends React.PureComponent {
  componentDidUpdate(prevProps) {
    const {
      position,
      isFlipped,
      recommendation,
      requestDataAction,
    } = this.props

    const isCurrent = recommendation && position === 'current'
    if (!isCurrent) return

    const shouldRequest =
      !prevProps.isFlipped && isFlipped && !recommendation.isClicked
    if (!shouldRequest) return

    const options = {
      key: 'recommendations',
      body: { isClicked: true },
    }
    requestDataAction('PATCH', `recommendations/${recommendation.id}`, options)
  }

  render() {
    const { currentHeaderColor, recommendation, position, width } = this.props
    const iscurrent = position === 'current'
    const translateTo = get(recommendation, 'index') * width
    return (
      <div
        className={`card ${iscurrent ? 'current' : ''}`}
        style={{
          backgroundColor: currentHeaderColor,
          transform: `translate(${translateTo}px, 0)`,
        }}
      >
        <Recto {...recommendation} />
        {iscurrent && <Verso />}
      </div>
    )
  }
}

Card.defaultProps = {
  isFlipped: false,
  recommendation: null,
  currentHeaderColor: '#000',
}

Card.propTypes = {
  isFlipped: PropTypes.bool,
  recommendation: PropTypes.object,
  width: PropTypes.number.isRequired,
  currentHeaderColor: PropTypes.string,
  position: PropTypes.string.isRequired,
  requestDataAction: PropTypes.func.isRequired,
}

const mapSizeToProps = ({ width, height }) => ({
  width: Math.min(width, 500), // body{max-width: 500px;}
  height,
})

export default compose(
  withSizes(mapSizeToProps),
  connect(
    null,
    { requestDataAction: requestData }
  )
)(Card)
