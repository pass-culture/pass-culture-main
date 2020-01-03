import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import Icon from '../Icon/Icon'

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
    const { dotFrequency } = this.props
    if (this.timer) window.clearInterval(this.timer)
    this.timer = window.setInterval(() => {
      const { nbDots } = this.state
      this.setState({
        nbDots: (nbDots % 3) + 1,
      })
    }, dotFrequency)
  }

  render() {
    const { label, Tag } = this.props
    const { nbDots } = this.state
    return (
      <Tag className="spinner">
        <Icon svg="ico-loader-r" />
        <span
          className="content"
          data-dots={Array(nbDots)
            .fill('.')
            .join('')}
        >
          {label}
        </span>
      </Tag>
    )
  }
}

Spinner.defaultProps = {
  Tag: 'div',
  dotFrequency: 500,
  label: 'Chargement',
}

Spinner.propTypes = {
  Tag: PropTypes.string,
  dotFrequency: PropTypes.number,
  label: PropTypes.string,
}

export default Spinner
