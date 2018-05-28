import classnames from 'classnames'
import React from 'react'
import { connect } from 'react-redux'

import OfferInfo from './OfferInfo'
import VersoWrapper from './VersoWrapper'
import MenuButton from './layout/MenuButton'
import selectCurrentMediation from '../selectors/currentMediation'
import selectIsCurrentTuto from '../selectors/isCurrentTuto'
import { THUMBS_URL } from '../utils/config'

const Verso = ({ mediation, isFlipped, isCurrentTuto }) => {
  return (
    <div
      className={classnames('verso', {
        flipped: isFlipped,
      })}
    >
      <VersoWrapper
        hasControlBar={!isCurrentTuto}
        className="with-padding-top"
      >
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

export default connect(state => ({
  mediation: selectCurrentMediation(state),
  isFlipped: state.verso.isFlipped,
  isCurrentTuto: selectIsCurrentTuto(state),
}))(Verso)
