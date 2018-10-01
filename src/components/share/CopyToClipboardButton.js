/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { CopyToClipboard } from 'react-copy-to-clipboard'

class CopyToClipboardButton extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = { copied: false }
  }

  toggleState = () => {
    const { onClick } = this.props
    this.setState(
      prev => ({ copied: !prev.copied }),
      () => {
        const { copied } = this.state
        onClick(copied)
      }
    )
  }

  render() {
    const { copied } = this.state
    const { className, value } = this.props
    return (
      <CopyToClipboard text={value} onCopy={this.toggleState}>
        <button
          type="button"
          className={`no-border no-background no-outline is-block ${className}`}
        >
          {/* <span
          aria-hidden
          className="icon-close mr7"
          title="Copier le lien de partage"
        /> */}
          {!copied && <span>Copier le lien</span>}
          {copied && <span>Fermer</span>}
        </button>
      </CopyToClipboard>
    )
  }
}

CopyToClipboardButton.defaultProps = {
  className: '',
}

CopyToClipboardButton.propTypes = {
  className: PropTypes.string,
  onClick: PropTypes.func.isRequired,
  value: PropTypes.string.isRequired,
}

export default CopyToClipboardButton
