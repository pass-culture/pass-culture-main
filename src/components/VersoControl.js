/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Logger, Icon, requestData } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose, bindActionCreators } from 'redux'

import ShareButton from './share/ShareButton'
import VersoBookingButton from './verso/VersoBookingButton'
import { getShareURL } from '../helpers'
import currentRecommendationSelector from '../selectors/currentRecommendation'

class VersoControl extends React.PureComponent {
  constructor(props) {
    super(props)
    const { dispatch } = this.props
    const actions = { requestData }
    this.actions = bindActionCreators(actions, dispatch)
  }

  componentWillMount() {
    Logger.fixme('VersoControl ---> componentWillMount')
  }

  componentWillUnmount() {
    Logger.fixme('VersoControl ---> componentWillUnmount')
  }

  onClickFavorite = () => {
    const { isFavorite, recommendationId } = this.props
    const method = 'PATCH'
    const url = `currentRecommendations/${recommendationId}`
    const opts = {
      body: { isFavorite: !isFavorite },
      key: 'currentRecommendations',
    }
    this.actions.requestData(method, url, opts)
  }

  render() {
    const { isFavorite, location, recommendation, user, wallet } = this.props

    const shareURL = getShareURL(location, user)
    const shareTitle = recommendation.offer.eventOrThing.name
    return (
      <ul className="verso-control">
        <li>
          <small className="pass-label">Mon Pass</small>
          <span className="pass-value">{wallet}€</span>
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
          <ShareButton shareURL={shareURL} shareTitle={shareTitle} />
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
  recommendation: null,
  recommendationId: null,
  wallet: null,
}

VersoControl.propTypes = {
  dispatch: PropTypes.func.isRequired,
  isFavorite: PropTypes.bool,
  location: PropTypes.object.isRequired,
  recommendation: PropTypes.object,
  recommendationId: PropTypes.string,
  user: PropTypes.object.isRequired,
  wallet: PropTypes.number,
}

const mapStateToProps = (state, ownProps) => {
  const { user } = state
  const { mediationId, offerId } = ownProps.match.params
  const { wallet_balance: wallet } = user
  const recommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )
  return {
    isFavorite: recommendation && recommendation.isFavorite,
    recommendation,
    recommendationId: recommendation.id,
    user,
    wallet,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VersoControl)
