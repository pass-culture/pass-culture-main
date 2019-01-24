import React from 'react'
import PropTypes from 'prop-types'
import { openSharePopin, closeSharePopin } from '../../reducers/share'
import MailToLink from '../layout/MailToLink'
import CopyToClipboardButton from './CopyToClipboardButton'

export const getCopyToClipboardButton = (url, onClick) => (
  <CopyToClipboardButton
    key="CopyToClipboard"
    value={url}
    className="py12 is-bold fs14"
    onClick={onClick}
  />
)
export const getMailToLinkButton = (email, headers) => (
  <MailToLink
    key="MailToLink"
    email={email}
    headers={headers}
    className="no-underline is-block is-white-text py12 is-bold fs14"
  >
    <span>
Envoyer par e-mail
    </span>
  </MailToLink>
)

export const getCloseButton = onClose => (
  <button
    key="closeButton"
    type="button"
    className="no-border no-background no-outline is-block py12 is-bold fs14"
    onClick={() => onClose()}
  >
    <span>
Fermer
    </span>
  </button>
)

class ShareButtonContent extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = { iscopied: false }
  }

  onCopyHandler = status => {
    this.setState({ iscopied: status }, () => {
      this.onClickShare()
    })
  }

  onCloseHandler = () => {
    const { dispatch } = this.props
    dispatch(closeSharePopin())
    this.setState({ iscopied: false })
  }

  onClickShare = () => {
    const { dispatch, email, offerName, text, url } = this.props

    try {
      const nativeOptions = { text: `${text}\n`, title: text, url }
      return navigator
        .share(nativeOptions)
        .then(() => {})
        .catch(() => {})
    } catch (err) {
      const headers = {
        body: `${text}\n\n${url}`,
        subject: text,
      }
      const popinOptions = {
        buttons: [
          getCopyToClipboardButton(url, this.onCopyHandler),
          getMailToLinkButton(email, headers),
        ],
        title: offerName,
        text: 'Comment souhaitez-vous partager cette offre ?',
      }

      const { iscopied } = this.state

      if (iscopied) {
        popinOptions.text = 'Le lien a bien été copié'
        popinOptions.buttons = [getCloseButton(this.onCloseHandler)]
      }

      return dispatch(openSharePopin(popinOptions))
    }
  }

  render() {
    const { offerName, url } = this.props
    const isDisabled = !offerName || !url
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
  email: null,
  offerName: null,
  text: null,
  url: null,
}

ShareButtonContent.propTypes = {
  dispatch: PropTypes.func.isRequired,
  email: PropTypes.string,
  offerName: PropTypes.string,
  text: PropTypes.string,
  url: PropTypes.string,
}

export default ShareButtonContent
