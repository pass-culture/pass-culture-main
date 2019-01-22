import React from 'react'
import PropTypes from 'prop-types'
import { openSharePopin } from '../../reducers/share'

class ShareButtonContent extends React.PureComponent {
  onClickShare = () => {
    const { dispatch, title, url, text } = this.props
    const options = { text, title, url }
    try {
      return navigator
        .share(options)
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

ShareButtonContent.defaultProps = {
  text: 'Comment souhaitez-vous partager cette offre ?',
  title: null,
  url: null,
}

ShareButtonContent.propTypes = {
  dispatch: PropTypes.func.isRequired,
  text: PropTypes.string,
  title: PropTypes.string,
  url: PropTypes.string,
}

export default ShareButtonContent
