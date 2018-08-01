import classnames from 'classnames'
import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import OfferInfo from './OfferInfo'
import VersoWrapper from './VersoWrapper'
import MenuButton from './layout/MenuButton'
import currentMediationSelector from '../selectors/currentMediation'
import isCurrentTutoSelector from '../selectors/isCurrentTuto'
import { THUMBS_URL } from '../utils/config'

const Verso = ({ isCurrentTuto, isFlipped, mediation }) => {
  return (
    <div
      className={classnames('verso', {
        flipped: isFlipped,
      })}>
      <VersoWrapper hasControlBar={!isCurrentTuto} className="with-padding-top">
        {isCurrentTuto ? (
          mediation && (
            <img
              alt="verso"
              className="verso-tuto-mediation"
              src={`${THUMBS_URL}/mediations/${mediation.id}_1`}
            />
          )
        ) : (
          <OfferInfo />
        )}
      </VersoWrapper>
      {isCurrentTuto ? (
        <MenuButton borderTop />
      ) : (
        <MenuButton borderTop colored />
      )}
    </div>
  )
}

export default compose(
  withRouter,
  connect(state => ({
    isCurrentTuto: isCurrentTutoSelector(state),
    isFlipped: state.verso.isFlipped,
    mediation: currentMediationSelector(state),
  }))
)(Verso)
