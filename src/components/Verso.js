import classnames from 'classnames'
import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import OfferInfo from './OfferInfo'
import VersoWrapper from './VersoWrapper'
import MenuButton from './layout/MenuButton'
import currentRecommendationSelector from '../selectors/currentRecommendation'
import { THUMBS_URL } from '../utils/config'

const Verso = ({
  currentRecommendation,
  isFlipped,
}) => {
  const {
    mediation
  } = (currentRecommendation || {})
  const {
    tutoIndex
  } = (mediation || {})

  console.log('VERSO', currentRecommendation)
  console.log('typeof tutoIndex', typeof tutoIndex)

  return (
    <div
      className={classnames('verso', {
        flipped: isFlipped,
      })}
    >
      <VersoWrapper className="with-padding-top">
        {typeof tutoIndex === 'number' ? (
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
      <MenuButton borderTop colored={typeof tutoIndex !== 'number'} />
    </div>
  )
}

export default compose(
  withRouter,
  connect((state, ownProps) => {
    const { mediationId, offerId } = ownProps.match.params
    return {
      isFlipped: state.verso.isFlipped,
      mediation: currentRecommendationSelector(state, offerId, mediationId),
    }
  })
)(Verso)
