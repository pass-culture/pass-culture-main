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
    addedValue.push(null)
    mergeForm(collectionName, entityId, name, addedValue)
  }

  deleteItem = item => {
    const {
      collectionName,
      defaultValue,
      entityId,
      mergeForm,
      name,
      value
    } = this.props
    const items = value || defaultValue
    const deletedValue = items.filter(i => i !== item)
    mergeForm(collectionName, entityId, name, deletedValue)
  }

  /*
  handleSetDefaultValue = () => {
    const {
      collectionName,
      defaultValue,
      entityId,
      mergeForm,
      name
    } = this.props
    entityId && mergeForm(collectionName, entityId, name, defaultValue)
  }

  componentDidMount () {
    this.handleSetDefaultValue()
  }

  componentDidUpdate (prevProps) {
    if (this.props.defaultValue && !prevProps.defaultValue) {
      this.handleSetDefaultValue()
    }
  }
  */

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
                  parentValue={items}
                />
              </div>
              <div className='control'>
                <a
                  className="button is-medium is-primary"
                  onClick={e => this.deleteItem(m)}
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
