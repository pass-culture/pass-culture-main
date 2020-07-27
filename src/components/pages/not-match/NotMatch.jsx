import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Redirect } from 'react-router-dom'
import Icon from '../../layout/Icon/Icon'

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

    if (timing < 0) return this.redirectTo()

    return (
      <div className="not-match">
        <Icon svg="404" />
        <span className="title">
          {'Oh non !'}
        </span>
        <span className="subtitle">
          {"Cette page n'existe pas"}
        </span>
        <span className="redirection-info">
          {timing > 0 ? `Tu vas être redirigé dans ${timing} secondes...` : 'Redirection...'}
        </span>
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
  redirect: PropTypes.string,
}

export default NotMatch
