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
import ActivationCard from './ActivationCard'

const Verso = ({
  currentRecommendation,
  areDetailsVisible,
  isWalletActivated,
}) => {
  const { mediation } = currentRecommendation || {}
  const { tutoIndex } = mediation || {}
  const isTuto = typeof tutoIndex === 'number' && mediation
  const useTutoImage = isTuto && isWalletActivated
  const useActivation = isTuto && !isWalletActivated && tutoIndex === 1
  return (
    <div
      className={classnames('verso', {
        flipped: areDetailsVisible,
      })}
    >
      <VersoWrapper className="with-padding-top">
        {!isTuto && <VersoInfo />}
        {useTutoImage && <StaticVerso mediationId={mediation.id} />}
        {useActivation && <ActivationCard mediationId={mediation.id} />}
      </VersoWrapper>
      <Footer borderTop colored={typeof tutoIndex !== 'number'} />
    </div>
  )
}

Verso.defaultProps = {
  currentRecommendation: null,
}

Verso.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  currentRecommendation: PropTypes.object,
  isWalletActivated: PropTypes.bool.isRequired,
}

export default compose(
  withRouter,
  connect((state, ownProps) => {
    const { mediationId, offerId } = ownProps.match.params
    const isWalletActivated = state.user.wallet_is_activated
    return {
      areDetailsVisible: state.card.areDetailsVisible,
      currentRecommendation: currentRecommendationSelector(
        state,
        offerId,
        mediationId
      ),
      isWalletActivated,
    }
  })
)(Verso)
