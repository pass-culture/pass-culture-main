/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React from 'react'
import { CopyToClipboard } from 'react-copy-to-clipboard'

class CopyToClipboardButton extends React.PureComponent {
  toggleState = () => {
    const { onClick } = this.props
    onClick(true)
  }

  render() {
    const { className, value } = this.props
    return (
      <CopyToClipboard text={value} onCopy={this.toggleState}>
        <button
          type="button"
          className={`no-border no-background no-outline is-block ${className}`}
        >
          <span>Copier le lien</span>
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
