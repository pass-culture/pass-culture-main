import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component } from 'react'

import Icon from './Icon'

class Spinner extends Component {
  constructor() {
    super()
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
    const { className, label, style, Tag } = this.props
    const { nbDots } = this.state
    return (
      <Tag
        className={classnames('spinner', className)}
        style={style}
      >
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
  className: null,
  dotFrequency: 500,
  label: 'Chargement',
  style: null,
}

Spinner.propTypes = {
  Tag: PropTypes.string,
  className: PropTypes.string,
  dotFrequency: PropTypes.number,
  label: PropTypes.string,
  style: PropTypes.object,
}

export default Spinner
