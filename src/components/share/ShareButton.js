import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'

import { getShareURL } from '../../helpers'
import { openSharePopin } from '../../reducers/share'

class ShareButton extends React.PureComponent {
  constructor(props) {
    super(props)
    const { dispatch } = this.props
    const actions = { openSharePopin }
    this.actions = bindActionCreators(actions, dispatch)
  }

  onClickShare = () => {
    const { location, recommendation, user } = this.props
    const shareURL = getShareURL(location, user)
    if (!shareURL || !recommendation) return null
    const shareTitle = recommendation.offer.eventOrThing.name
    const nativeShare =
      Navigator.share || navigator.share || window.navigator.share
    const options = {
      text: 'Comment souhaitez-vous partager cette offre ?',
      title: shareTitle,
      url: shareURL,
    }
    if (!nativeShare) return this.actions.openSharePopin(options)
    return nativeShare(options)
      .then(() => console.log('Successful share'))
      .catch(error => console.log('Error sharing', error))
  }

  render() {
    return (
      <button
        type="button"
        className="button is-secondary fs32"
        onClick={this.onClickShare}
      >
        <span aria-hidden className="icon-share" title="Partager cette offre" />
      </button>
    )
  }
}

ShareButton.propTypes = {
  dispatch: PropTypes.func.isRequired,
  location: PropTypes.object.isRequired,
  recommendation: PropTypes.object.isRequired,
  user: PropTypes.object.isRequired,
}

export default connect()(ShareButton)
