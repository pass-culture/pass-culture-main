import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { openSharePopin } from '../../reducers/share'

class ShareButton extends React.PureComponent {
  onClickShare = () => {
    const { dispatch, shareTitle, shareURL, shareDescription } = this.props
    const nativeShare =
      Navigator.share || navigator.share || window.navigator.share
    const options = {
      text: shareDescription,
      title: shareTitle,
      url: shareURL,
    }
    if (!nativeShare) return dispatch(openSharePopin(options))
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
