import React, { Component } from 'react'

class Select extends Component {
  constructor () {
    super()
    this.onOptionClick = this._onOptionClick.bind(this)
  }
  _onOptionClick () {

  }
  render () {
    const { selectedOption, options } = this.props
    return (
      <select className='select'>
        <option key={-1} disabled selected value>
          -- select an option --
        </option>
        {
          options.map(({ label, value }, index) => (
            <option key={index}
              onClick={value => this.onOptionClick(value)}
              value={value}
            >
              {label}
            </option>
          ))
        }
      </select>
    )
  }
}

export default Select
