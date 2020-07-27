import React, { PureComponent } from 'react'
import { Redirect } from 'react-router-dom'
import { ROOT_PATH } from '../../../utils/config'

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
  renderRedirecting = () => (<span>
    {'Redirection...'}
  </span>)

  renderTimer = timing => (<span>
    {`Vous allez être redirigé dans ${timing} secondes`}
  </span>)

  render() {
    const { timing } = this.state
    if (timing < 0) return this.renderRedirect()
    return (
      <div className="page fullscreen no-match">
        <img
          alt=""
          src={`${ROOT_PATH}/icons/ico-404.svg`}
        />
        <h1>
          {'Oh non !'}
        </h1>
        <p className="subtitle">
          {"Cette page n'existe pas."}
        </p>
        <p className="redirection-info">
          {timing > 0 && this.renderTimer(timing)}
          {timing === 0 && this.renderRedirecting()}
        </p>
      </div>
    )
  }
}

export default NoMatch
