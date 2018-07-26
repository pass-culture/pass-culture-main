import { Icon } from 'pass-culture-shared'
import classnames from 'classnames'
import React, { Component } from 'react'


class Loader extends Component {

  constructor() {
    super()
    this.state = {
      nbDots: 3,
    }
  }

  static defaultProps = {
    Tag: 'div',
    label: 'Chargement',
    dotFrequency: 500,
  }

  startDots = () => {
    if (this.timer)
      window.clearInterval(this.timer)
    this.timer = window.setInterval(() => {
      this.setState({
        nbDots: (this.state.nbDots) % 3 + 1
      })
    }, this.props.dotFrequency)
  }

  componentDidMount() {
    this.startDots()
  }

  componentWillUnmount() {
    window.clearInterval(this.timer)
  }

  render() {
    const {
      className,
      label,
      style,
      Tag,
    } = this.props
    return (
      <Tag className={classnames("pc-loader", className)} style={style}>
        <Icon svg='loader-r' />
        <span className='content' data-dots={Array(this.state.nbDots).fill('.').join('')}>{label}</span>
      </Tag>
    )
  }
}

export default Loader
