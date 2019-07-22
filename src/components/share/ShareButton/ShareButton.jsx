import PropTypes from 'prop-types'
import React from 'react'

import CopyToClipboardButton from '../CopyToClipboardButton'
import MailToLink from '../../layout/MailToLink'
import { openSharePopin, closeSharePopin } from '../../../reducers/share'

class ShareButton extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = { iscopied: false }
  }

  getCopyToClipboardButton = (url, onClick) => (
    <CopyToClipboardButton
      className="py12 is-bold fs14"
      key="CopyToClipboard"
      onClick={onClick}
      value={url}
    />
  )

  getMailToLinkButton = (email, headers) => (
    <MailToLink
      className="no-underline is-block is-white-text py12 is-bold fs14"
      email={email}
      headers={headers}
      key="MailToLink"
    >
      <span>{'Envoyer par e-mail'}</span>
    </MailToLink>
  )

  getCloseButton = onClose => (
    <button
      className="no-border no-background no-outline is-block py12 is-bold fs14"
      key="closeButton"
      onClick={onClose}
      type="button"
    >
      <span>{'Fermer'}</span>
    </button>
  )

  onCopyHandler = status => {
    this.setState({ iscopied: status }, () => {
      this.handleOnClickShare()
    })
  }

  onCloseHandler = () => {
    const { dispatch } = this.props
    dispatch(closeSharePopin())
    this.setState({ iscopied: false })
  }

  handleOnClickShare = () => {
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
          this.getCopyToClipboardButton(url, this.onCopyHandler),
          this.getMailToLinkButton(email, headers),
        ],
        text: 'Comment souhaitez-vous partager cette offre ?',
        title: offerName,
      }

      const { iscopied } = this.state

      if (iscopied) {
        popinOptions.text = 'Le lien a bien été copié.'
        popinOptions.buttons = [this.getCloseButton(this.onCloseHandler)]
      }

      return dispatch(openSharePopin(popinOptions))
    }
  }

  render() {
    const { id, offerName, url } = this.props
    const isDisabled = !offerName || !url
    return (
      <button
        className="no-border no-background"
        disabled={isDisabled}
        id={id}
        onClick={this.handleOnClickShare}
        type="button"
      >
        <span
          aria-hidden
          className="font-icon icon-ico-share"
          title="Partager cette offre"
        />
      </button>
    )
  }
}

ShareButton.defaultProps = {
  email: null,
  id: 'verso-share-button',
  offerName: null,
  text: null,
  url: null,
}

ShareButton.propTypes = {
  dispatch: PropTypes.func.isRequired,
  email: PropTypes.string,
  id: PropTypes.string,
  offerName: PropTypes.string,
  text: PropTypes.string,
  url: PropTypes.string,
}

export default ShareButton
