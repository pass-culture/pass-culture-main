import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Redirect } from 'react-router-dom'

class NotMatch extends PureComponent {
  constructor(props) {
    super(props)
    this.timer = null
    this.state = { timing: props.delay }
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

  redirectTo = () => {
    const { redirect } = this.props
    return <Redirect to={redirect} />
  }

  render() {
    const { timing } = this.state
    const { location } = this.props

    if (timing < 0) return this.redirectTo()

    return (
      <div className="page">
        <h3>
          {`404 Not found ${location.pathname}`}
        </h3>
        <p>
          {timing > 0
            ? `Vous allez être automatiquement redirigé dans ${timing} secondes.`
            : 'Redirection...'}
        </p>
      </div>
    )
  }
}

NotMatch.defaultProps = {
  delay: 5,
  redirect: '/',
}

NotMatch.propTypes = {
  delay: PropTypes.number,
  location: PropTypes.shape().isRequired,
  redirect: PropTypes.string,
}

export default NotMatch
