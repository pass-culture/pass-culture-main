import PropTypes from 'prop-types'
import React, { Component } from 'react'
import classnames from 'classnames'

class DisplayButton extends Component {
  constructor(props) {
    super(props)
    this.state = {
      isLoading: false,
    }
  }

  handleRequestData = () => {
    const { downloadFileOrNotifyAnError, history, location, showFailureNotification } = this.props
    this.setState({ isLoading: true }, async () => {
      const dataFromCsv = await downloadFileOrNotifyAnError()
      const { data } = dataFromCsv
      this.setState({ isLoading: false })
      const { pathname } = location
      const redirectUrl = pathname + '/detail'
      const hasAtLeastData = data.length > 0

      if (hasAtLeastData) {
        history.push(redirectUrl, dataFromCsv)
      } else {
        showFailureNotification()
      }
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
        onClick={this.handleRequestData}
        type="button"
      >
        {children}
      </button>
    )
  }
}

DisplayButton.propTypes = {
  children: PropTypes.string,
  downloadFileOrNotifyAnError: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  location: PropTypes.shape().isRequired,
  showFailureNotification: PropTypes.func.isRequired,
}

export default DisplayButton
