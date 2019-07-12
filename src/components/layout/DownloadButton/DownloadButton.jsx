import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

class DownloadButton extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { isLoading: false }
  }

  handleOnClick = () => () => {
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
        className={classnames('button is-primary', {
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

DownloadButton.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node,
  ]),
  downloadFileOrNotifyAnError: PropTypes.func.isRequired,
}

export default DownloadButton
