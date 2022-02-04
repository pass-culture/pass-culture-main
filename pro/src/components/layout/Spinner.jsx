import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import Icon from './Icon'

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
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
    const { message } = this.props

    return (
      <div className="loading-spinner" data-testid="spinner">
        <Icon svg="loader-pc" />
        <div className="content" data-dots={Array(nbDots).fill('.').join('')}>
          {message}
        </div>
      </div>
    )
  }
}

Spinner.defaultProps = {
  message: 'Chargement en cours',
}

Spinner.propTypes = {
  message: PropTypes.string,
}

export default Spinner
