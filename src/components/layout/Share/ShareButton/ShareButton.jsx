import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import CopyToClipboardButton from '../CopyToClipboardButton'
import Icon from '../../Icon/Icon'
import MailToLink from '../../MailToLink/MailToLink'

class ShareButton extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { isCopied: false }
  }

  getCopyToClipboardButton = (url, onClick) => (
    <CopyToClipboardButton
      key="CopyToClipboard"
      onClick={onClick}
      value={url}
    />
  )

  getMailToLinkButton = (email, headers, trackShareOffer) => (
    <MailToLink
      className="no-underline is-white-text py12 is-bold fs14"
      email={email}
      headers={headers}
      key="MailToLink"
      onClick={trackShareOffer}
    >
      {'Envoyer par e-mail'}
    </MailToLink>
  )

  getCloseButton = onClose => (
    <button
      className="no-background py12 is-bold fs14"
      key="closeButton"
      onClick={onClose}
      type="button"
    >
      {'Fermer'}
    </button>
  )

  onCopyHandler = status => {
    const { trackShareOfferByLink } = this.props
    trackShareOfferByLink()
    this.setState({ isCopied: status }, () => {
      this.handleOnClickShare()
    })
  }

  onCloseHandler = () => {
    const { closePopin } = this.props
    closePopin()
    this.setState({ isCopied: false })
  }

  handleOnClickShare = () => {
    const { email, offerName, openPopin, text, url, trackShareOfferByMail } = this.props

    try {
      const nativeOptions = { text: `${text}\n`, title: text, url }

      return navigator.share(nativeOptions)
    } catch (err) {
      const { isCopied } = this.state
      const headers = {
        body: `${text}\n\n${url}`,
        subject: text,
      }
      const popinOptions = {
        buttons: [
          this.getCopyToClipboardButton(url, this.onCopyHandler),
          this.getMailToLinkButton(email, headers, trackShareOfferByMail),
        ],
        text: 'Comment souhaitez-vous partager cette offre ?',
        title: offerName,
      }

      if (isCopied) {
        popinOptions.text = 'Le lien a bien été copié.'
        popinOptions.buttons = [this.getCloseButton(this.onCloseHandler)]
      }

      return openPopin(popinOptions)
    }
  }

  render() {
    return (
      <button
        className="no-background"
        onClick={this.handleOnClickShare}
        type="button"
      >
        <Icon
          alt="Partager cette offre"
          svg="ico-share-w"
        />
      </button>
    )
  }
}

ShareButton.defaultProps = {
  email: null,
  offerName: null,
  text: null,
  url: null,
}

ShareButton.propTypes = {
  closePopin: PropTypes.func.isRequired,
  email: PropTypes.string,
  offerName: PropTypes.string,
  openPopin: PropTypes.func.isRequired,
  text: PropTypes.string,
  trackShareOfferByLink: PropTypes.func.isRequired,
  trackShareOfferByMail: PropTypes.func.isRequired,
  url: PropTypes.string,
}

export default ShareButton
