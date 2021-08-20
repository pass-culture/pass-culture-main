import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
class DownloadButton extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { isLoading: false }
  }

  handleOnClick = () => {
    const { downloadFileOrNotifyAnError } = this.props
    this.setState({ isLoading: true }, async () => {
      await downloadFileOrNotifyAnError()
      this.setState({ isLoading: false })
    })
  }

  render() {
    const { children, isDisabled } = this.props
    const { isLoading } = this.state

    return (
      <button
        className={classnames('primary-button', {
          'is-loading': isLoading,
        })}
        disabled={isLoading || isDisabled}
        download
        onClick={this.handleOnClick}
        type="button"
      >
        {children}
      </button>
    )
  }
}

DownloadButton.defaultProps = {
  children: '',
  isDisabled: false,
}

DownloadButton.propTypes = {
  children: PropTypes.string,
  downloadFileOrNotifyAnError: PropTypes.func.isRequired,
  isDisabled: PropTypes.bool,
}

export default DownloadButton
