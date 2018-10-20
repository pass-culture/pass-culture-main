import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { openSharePopin } from '../../reducers/share'

class ShareButton extends React.PureComponent {
  onClickShare = () => {
    const { dispatch, shareTitle, shareURL, shareDescription } = this.props
    const options = {
      text: shareDescription,
      title: shareTitle,
      url: shareURL,
    }
    try {
      const nativeShare = window.navigator.share || navigator.share
      return nativeShare(options)
        .then(() => console.log('Successful share'))
        .catch(error => console.log('Error sharing', error))
    } catch (err) {
      return dispatch(openSharePopin(options))
    }
  }

  render() {
    return (
      <button
        type="button"
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
  shareDescription: 'Comment souhaitez-vous partager cette offre ?',
}

ShareButton.propTypes = {
  dispatch: PropTypes.func.isRequired,
  shareDescription: PropTypes.string,
  shareTitle: PropTypes.string.isRequired,
  shareURL: PropTypes.string.isRequired,
}

export default connect()(ShareButton)
