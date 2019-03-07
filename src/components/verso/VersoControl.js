/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Icon, requestData } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose, bindActionCreators } from 'redux'

import { getWalletValue } from '../../utils/user'
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
    const { isFavorite, walletValue } = this.props
    return (
      <ul className="verso-control">
        <li>
          <small className="pass-label">Mon Pass</small>
          <span id="verso-wallet-value" className="pass-value">
            {walletValue}&nbsp;€
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
}

VersoControl.propTypes = {
  dispatch: PropTypes.func.isRequired,
  isFavorite: PropTypes.bool,
  recommendationId: PropTypes.string,
  walletValue: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
    .isRequired,
}

const mapStateToProps = (state, ownProps) => {
  const { user } = state
  const { mediationId, offerId } = ownProps.match.params
  const recommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )
  const walletValue = getWalletValue(user)
  return {
    isFavorite: recommendation && recommendation.isFavorite,
    recommendationId: recommendation && recommendation.id,
    walletValue,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VersoControl)
