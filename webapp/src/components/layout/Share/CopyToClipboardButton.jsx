import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { CopyToClipboard } from 'react-copy-to-clipboard'

class CopyToClipboardButton extends PureComponent {
  handleToggleState = () => {
    const { onClick } = this.props
    onClick(true)
  }

  render() {
    const { value } = this.props

    return (
      <CopyToClipboard
        onCopy={this.handleToggleState}
        text={value}
      >
        <button
          className="no-background py12 is-bold fs14"
          type="button"
        >
          {'Copier le lien'}
        </button>
      </CopyToClipboard>
    )
  }
}

CopyToClipboardButton.propTypes = {
  onClick: PropTypes.func.isRequired,
  value: PropTypes.string.isRequired,
}

export default CopyToClipboardButton
