import React, {Component} from 'react'
import { optionify } from '../../../utils/form'
import get from 'lodash.get'
import classnames from 'classnames'


class SelectInput extends Component {

  componentDidMount() {
    this.handleUniqueSelectOption()
  }

  componentDidUpdate(prevProps) {
    if (prevProps.options !== this.props.options) {
      this.handleUniqueSelectOption()
    }
  }

  render() {
    const onChange = e => this.props.onChange(e.target.value)

    const handleUniqueSelectOption = () => {
      const { options, optionValue } = this.props
      if (options && options.length === 1) {
        onChange(options[0][optionValue])
      }
    }

    const actualReadOnly = this.props.readOnly || this.props.options.length === 1
    const actualOptions = optionify(this.props.options.map(o => ({label: get(o, this.props.optionLabel), value: get(o, this.props.optionValue)})), this.props.placeholder)

    return <div className={`select is-${this.props.size} ${classnames({readonly: this.props.actualReadOnly})}`}>
      <select
        {...this.props}
        onChange={onChange}
        disabled={this.props.actualReadOnly} // readonly doesn't exist on select
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

