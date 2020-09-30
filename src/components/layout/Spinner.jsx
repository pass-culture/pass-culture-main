import React, { PureComponent } from 'react'

import Icon from './Icon'

class Spinner extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      nbDots: 3,
    }
  }

  componentDidMount() {
    this.startDots()
  }

  componentWillUnmount() {
    window.clearInterval(this.timer)
  }

  startDots = () => {
    if (this.timer) window.clearInterval(this.timer)
    this.timer = window.setInterval(() => {
      const { nbDots } = this.state
      this.setState({
        nbDots: (nbDots % 3) + 1,
      })
    }, 500)
  }

  render() {
    const { nbDots } = this.state
    return (
      <div className="loading-spinner">
        <Icon svg="loader-pc" />
        <div
          className="content"
          data-dots={Array(nbDots).fill('.').join('')}
        >
          {'Chargement en cours'}
        </div>
      </div>
    )
  }
}

export default Spinner
