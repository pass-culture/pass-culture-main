/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Icon, requestData } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose, bindActionCreators } from 'redux'

import { ShareButton } from '../share/ShareButton'
import VersoBookingButton from './VersoBookingButton'
import currentRecommendationSelector from '../../selectors/currentRecommendation'

class VersoControl extends React.PureComponent {
  constructor(props) {
    super(props)
    const { dispatch } = this.props
    const actions = { requestData }
    this.actions = bindActionCreators(actions, dispatch)
  }

  onClickFavorite = () => {
    const { isFavorite, recommendationId } = this.props
    const url = `currentRecommendations/${recommendationId}`
    this.actions.requestData('PATCH', url, {
      body: { isFavorite: !isFavorite },
      key: 'currentRecommendations',
    })
  }

  render() {
    const { isFavorite, wallet } = this.props
    return (
      <ul className="verso-control">
        <li>
          <small className="pass-label">Mon Pass</small>
          <span id="verso-wallet-value" className="pass-value">
            {wallet}€
          </span>
        </li>
        <li>
          <button
            disabled
            type="button"
            className="button is-secondary"
            onClick={this.onClickFavorite}
          >
            <Icon
              alt={isFavorite ? 'Retirer des favoris' : 'Ajouter aux favoris'}
              svg={isFavorite ? 'ico-like-w-on' : 'ico-like-w'}
            />
          </button>
        </li>
        <li>
          <ShareButton />
        </li>
        <li>
          <VersoBookingButton />
        </li>
      </ul>
    )
  }
}

VersoControl.defaultProps = {
  isFavorite: false,
  recommendationId: null,
  wallet: null,
}

VersoControl.propTypes = {
  dispatch: PropTypes.func.isRequired,
  isFavorite: PropTypes.bool,
  recommendationId: PropTypes.string,
  wallet: PropTypes.number,
}

const mapStateToProps = (state, ownProps) => {
  const { user } = state
  const { mediationId, offerId } = ownProps.match.params
  const recommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )
  const wallet =
    user && typeof user.wallet_balance === 'number' ? user.wallet_balance : '--'
  return {
    isFavorite: recommendation && recommendation.isFavorite,
    recommendationId: recommendation && recommendation.id,
    wallet,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VersoControl)
