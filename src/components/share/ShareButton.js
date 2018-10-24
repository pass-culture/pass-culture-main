import React from 'react'
import PropTypes from 'prop-types'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import currentRecommendationSelector from '../../selectors/currentRecommendation'
import { getShareURL } from '../../helpers'
import { openSharePopin } from '../../reducers/share'

class ShareButton extends React.PureComponent {
  onClickShare = () => {
    const { dispatch, title, url, text } = this.props
    const options = { text, title, url }
    try {
      const nativeShare = window.navigator.share || navigator.share
      return nativeShare(options)
        .then(() => {})
        .catch(() => {})
    } catch (err) {
      return dispatch(openSharePopin(options))
    }
  }

  render() {
    const { title, url } = this.props
    const isDisabled = !title || !url
    return (
      <button
        type="button"
        disabled={isDisabled}
        className="button is-secondary fs32"
        onClick={this.onClickShare}
      >
        <span
          aria-hidden
          className="icon-legacy-share"
          title="Partager cette offre"
        />
      </button>
    )
  }
}

ShareButton.defaultProps = {
  text: 'Comment souhaitez-vous partager cette offre ?',
  title: null,
  url: null,
}

ShareButton.propTypes = {
  dispatch: PropTypes.func.isRequired,
  text: PropTypes.string,
  title: PropTypes.string,
  url: PropTypes.string,
}

const mapStateToProps = (state, ownProps) => {
  const { user } = state
  const { location } = ownProps
  const { mediationId, offerId } = ownProps.match.params
  const recommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )
  const url = (user && getShareURL(location, user)) || null
  const title =
    (recommendation && recommendation.offer.eventOrThing.name) || null
  return { title, url }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(ShareButton)
