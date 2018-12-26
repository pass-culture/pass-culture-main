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
import { THUMBS_URL } from '../../utils/config'

const Verso = ({ currentRecommendation, areDetailsVisible }) => {
  const { mediation } = currentRecommendation || {}
  const { tutoIndex } = mediation || {}
  return (
    <div
      className={classnames('verso', {
        flipped: areDetailsVisible,
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
          <VersoInfo />
        )}
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
}

export default compose(
  withRouter,
  connect((state, ownProps) => {
    const { mediationId, offerId } = ownProps.match.params
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
