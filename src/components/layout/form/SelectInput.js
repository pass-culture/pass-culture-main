import classnames from 'classnames'
import get from 'lodash.get'
import React, { Component } from 'react'

import { optionify } from '../../../utils/form'


class SelectInput extends Component {

  componentDidMount() {
    this.handleUniqueSelectOption()
  }

  componentDidUpdate(prevProps) {
    if (prevProps.options !== this.props.options) {
      this.handleUniqueSelectOption()
    }
  }

  handleUniqueSelectOption = () => {
    const { options, optionValue } = this.props
    if (options && options.length === 1) {
      this.props.onChange(options[0][optionValue])
    }
  }

  onChange = e => this.props.onChange(e.target.value)

  render() {

    const actualReadOnly = this.props.readOnly || this.props.options.length === 1
    const actualOptions = optionify(this.props.options.map(o => ({label: get(o, this.props.optionLabel), value: get(o, this.props.optionValue)})), this.props.placeholder)

    return <div className={`select is-${this.props.size} ${classnames({readonly: actualReadOnly})}`}>
      <select
        aria-describedby={this.props['aria-describedby']}
        autoComplete={this.props.autoComplete}
        id={this.props.id}
        name={this.props.name}
        required={this.props.required}
        type={this.props.type}
        value={this.props.value}
        onChange={this.onChange}
        disabled={actualReadOnly} // readonly doesn't exist on select
        >
        { actualOptions.filter(o => o).map(({ label, value }, index) =>
          <option key={index} value={value}>
            {label}
          </option>
        )}
      </select>
    </div>
  }
}

SelectInput.defaultProps = {
  optionValue: 'id',
  optionLabel: 'name',
}

export default SelectInput
