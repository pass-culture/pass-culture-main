import PropTypes from 'prop-types'
import classnames from 'classnames'
import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Footer from '../layout/Footer'
import VersoInfo from './VersoInfo'
import VersoWrapper from './VersoWrapper'
import currentRecommendationSelector from '../../selectors/currentRecommendation'
import StaticVerso from './StaticVerso'

const Verso = ({
  areDetailsVisible,
  forceDetailsVisible,
  className,
  currentRecommendation,
}) => {
  const { mediation } = currentRecommendation || {}
  const { tutoIndex } = mediation || {}
  const isTuto = typeof tutoIndex === 'number' && mediation

  const flipped = forceDetailsVisible || areDetailsVisible

  return (
    <div
      className={classnames('verso', className, {
        flipped,
      })}
    >
      <VersoWrapper className="with-padding-top">
        {!isTuto && <VersoInfo />}
        {isTuto && <StaticVerso mediationId={mediation.id} />}
      </VersoWrapper>
      <Footer borderTop colored={typeof tutoIndex !== 'number'} />
    </div>
  )
}

Verso.defaultProps = {
  className: null,
  currentRecommendation: null,
  forceDetailsVisible: false,
}

Verso.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  className: PropTypes.string,
  currentRecommendation: PropTypes.object,
  forceDetailsVisible: PropTypes.bool,
}

export default compose(
  withRouter,
  connect((state, ownProps) => {
    const { match } = ownProps
    const {
      params: { mediationId, offerId },
    } = match

    return {
      areDetailsVisible: state.card.areDetailsVisible,
      currentRecommendation: currentRecommendationSelector(
        state,
        offerId,
        mediationId
      ),
    }
  })
)(Verso)
