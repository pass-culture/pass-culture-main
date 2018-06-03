import classnames from 'classnames'
import React, { Component } from 'react'

class SwitchButton extends Component {
  constructor (props) {
    super()
    this.state = { isSwitched: props.isInitialActive }
  }

  onClick = event => {
    this.setState({ isSwitched: !this.state.isSwitched })
    event.target.value = !this.state.isSwitched
    this.props.onClick && this.props.onClick(event)
  }

  render () {
    const {
      className,
      OnElement,
      OffElement
    } = this.props
    const { isSwitched } = this.state
    return (
      <button
        className={classnames({
          'switch-button--off': !isSwitched,
          'switch-button--on': isSwitched
        }, className)}
        onClick={this.onClick}
      >
        <div>
          { isSwitched ? OnElement : OffElement}
        </div>
      </button>
    )
  }
}

SwitchButton.defaultProps = {
  className: 'switch-button',
  OffElement: <p> OFF </p>,
  OnElement: <p> ON </p>
}

export default SwitchButton
