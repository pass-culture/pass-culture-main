import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Redirect } from 'react-router-dom'

class NoMatch extends PureComponent {
  constructor(props) {
    super(props)
    this.timer = null
    this.state = { timing: 5 }
  }

  componentDidMount() {
    const timeout = 1000
    this.timer = setInterval(() => {
      this.setState(({ timing }) => ({ timing: timing - 1 }))
    }, timeout)
  }

  componentWillUnmount() {
    if (this.timer) clearInterval(this.timer)
    this.timer = null
  }

  renderRedirect = () => <Redirect to="/" />
  renderRedirecting = () => (
    <span>
      {'Redirecting...'}
    </span>
  )

  renderTimer = timing => (
    <span>
      {`You will be redirect in ${timing} seconds`}
    </span>
  )

  render() {
    const { timing } = this.state
    const { location } = this.props
    if (timing < 0) return this.renderRedirect()
    return (
      <div id="page-redirect">
        <h3 className="title">
          {`404 Not found ${location.pathname}`}
        </h3>
        <p className="content">
          {timing > 0 && this.renderTimer(timing)}
          {timing === 0 && this.renderRedirecting()}
        </p>
      </div>
    )
  }
}

NoMatch.propTypes = {
  location: PropTypes.shape().isRequired,
}

export default NoMatch
