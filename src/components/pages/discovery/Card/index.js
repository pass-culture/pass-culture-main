import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import withSizes from 'react-sizes'
import { compose } from 'redux'

import { mapDispatchToProps, mapStateToProps } from './connect'
import Recto from '../../../Recto'
import Verso from '../../../verso'
import { getHeaderColor } from '../../../../utils/colors'

export class RawCard extends PureComponent {
  componentDidMount() {
    const { handleReadRecommendation, position, recommendation } = this.props

    const isFirstHasJustBeenRead = position === 'previous'
    if (isFirstHasJustBeenRead) {
      handleReadRecommendation(recommendation)
    }
  }

  componentDidUpdate(prevProps) {
    const {
      handleClickRecommendation,
      handleReadRecommendation,
      isFlipped,
      recommendation,
      position,
    } = this.props

    const isCurrent = recommendation && position === 'current'

    const hasJustBeenRead =
      position === 'previous' &&
      (recommendation && recommendation.id) !==
        (prevProps.recommendation && prevProps.recommendation.id)
    if (hasJustBeenRead) {
      handleReadRecommendation(recommendation)
    }

    if (!isCurrent) return

    const shouldRequest =
      !prevProps.isFlipped && isFlipped && !recommendation.isClicked
    if (!shouldRequest) return

    handleClickRecommendation(recommendation)
  }

  render() {
    const { position, recommendation, width } = this.props
    const firstThumbDominantColor =
      recommendation && recommendation.firstThumbDominantColor
    const headerColor = getHeaderColor(firstThumbDominantColor)

    const { index } = recommendation || {}
    const iscurrent = position === 'current'
    const translateTo = index * width
    return (
      <div
        className={`card ${iscurrent ? 'current' : ''}`}
        style={{
          backgroundColor: headerColor || '#000',
          transform: `translate(${translateTo}px, 0)`,
        }}
      >
        {iscurrent && <Verso />}
        <Recto position={position} />
      </div>
    )
  }
}

RawCard.defaultProps = {
  isFlipped: false,
  recommendation: null,
}

RawCard.propTypes = {
  handleClickRecommendation: PropTypes.func.isRequired,
  handleReadRecommendation: PropTypes.func.isRequired,
  isFlipped: PropTypes.bool,
  position: PropTypes.string.isRequired,
  recommendation: PropTypes.object,
  width: PropTypes.number.isRequired,
}

const mapSizeToProps = ({ width, height }) => ({
  height,
  width: Math.min(width, 500), // body{max-width: 500px;}
})

export default compose(
  withSizes(mapSizeToProps),
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(RawCard)
