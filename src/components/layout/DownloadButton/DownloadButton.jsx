import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

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
    const { children } = this.props
    const { isLoading } = this.state

    return (
      <button
        className={classnames('primary-button', {
          'is-loading': isLoading,
        })}
        disabled={isLoading}
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
}

DownloadButton.propTypes = {
  children: PropTypes.string,
  downloadFileOrNotifyAnError: PropTypes.func.isRequired,
}

export default DownloadButton
