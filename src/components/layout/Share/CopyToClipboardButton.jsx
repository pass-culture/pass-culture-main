import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { CopyToClipboard } from 'react-copy-to-clipboard'

class CopyToClipboardButton extends PureComponent {
  handleToggleState = () => {
    const { onClick } = this.props
    onClick(true)
  }

  render() {
    const { className, value } = this.props

    return (
      <CopyToClipboard
        onCopy={this.handleToggleState}
        text={value}
      >
        <button
          className={`no-background ${className}`}
          type="button"
        >
          {'Copier le lien'}
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
