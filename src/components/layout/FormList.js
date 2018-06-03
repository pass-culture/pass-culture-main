import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormInput from './FormInput'
import { getFormValue, mergeForm } from '../../reducers/form'

class FormList extends Component {

  addItem = () => {
    const {
      collectionName,
      defaultValue,
      entityId,
      mergeForm,
      name,
      value
    } = this.props
    const items = value || defaultValue
    const addedValue = items
      ? [...items]
      : []
    addedValue.push('')
    mergeForm(collectionName, entityId, name, addedValue)
  }

  deleteItem = index => {
    const {
      collectionName,
      defaultValue,
      entityId,
      mergeForm,
      name,
      value
    } = this.props
    const items = value || defaultValue
    const deletedValue = [...items]
    delete deletedValue[index]
    mergeForm(collectionName, entityId, name, deletedValue)
  }

  render () {
    const {
      addText,
      defaultValue,
      name,
      value
    } = this.props
    const items = value || defaultValue
    return (
      <ul>
        {
          Object.values(items || {}).map((m, i) => (
            <li className='field has-addons' key={i}>
              <div className='control is-expanded'>
                <FormInput
                  {...this.props}
                  defaultValue={m}
                  name={`${name}.${i}`}
                />
              </div>
              <div className='control'>
                <a
                  className="button is-medium is-primary"
                  onClick={e => this.deleteItem(i)}
                >
                  &nbsp;
                  <span className='delete'/>
                  &nbsp;
                </a>
              </div>
            </li>
          ))
        }
        <li className='has-text-right'>
          <button
            className='button is-primary is-outlined is-small'
            onClick={this.addItem}>
              {addText}
          </button>
        </li>
      </ul>
    )
  }
}

FormList.defaultProps = {
  addText: 'Ajouter'
}

export default connect(
  (state, ownProps) => ({ value: getFormValue(state, ownProps) }),
  { mergeForm }
)(FormList)
