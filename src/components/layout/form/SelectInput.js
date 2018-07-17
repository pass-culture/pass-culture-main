import React from 'react'
import { optionify } from '../../../utils/form'
import get from 'lodash.get'
import classnames from 'classnames'


const SelectInput = props => {

  const onChange = e => props.onChange(e.target.value)

  const actualReadOnly = props.readOnly || props.options.length === 1
  const actualOptions = optionify(props.options.map(o => ({label: get(o, props.optionLabel), value: get(o, props.optionValue)})), props.placeholder)

  return <div className={`select is-${props.size} ${classnames({readonly: props.actualReadOnly})}`}>
    <select
      {...props}
      onChange={onChange}
      disabled={props.actualReadOnly} // readonly doesn't exist on select
      >
      { actualOptions.filter(o => o).map(({ label, value }, index) =>
        <option key={index} value={value}>
          {label}
        </option>
      )}
    </select>
  </div>
}

SelectInput.defaultProps = {
  optionValue: 'id',
  optionLabel: 'name',
}

export default SelectInput

