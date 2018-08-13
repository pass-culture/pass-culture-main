import React from 'react'
import PropTypes from 'prop-types'
import { Redirect } from 'react-router-dom'

const renderRedirect = () => <Redirect to="/" />
const renderRedirecting = () => (
  <span>
    {'Redirecting...'}
  </span>
)

const renderTimer = timing => (
  <span>
    {`You will be redirect in ${timing} seconds`}
  </span>
)

class NoMatch extends React.PureComponent {
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

  render() {
    const { timing } = this.state
    const { location } = this.props
    if (timing < 0) return renderRedirect()
    return (
      <div id="page-redirect">
        <h3 className="title">
          {`404 Not found ${location.pathname}`}
        </h3>
        <p className="content">
          {timing > 0 && renderTimer(timing)}
          {timing === 0 && renderRedirecting()}
        </p>
      </div>
    )
  }
}

NoMatch.propTypes = {
  location: PropTypes.object.isRequired,
}

export default NoMatch
