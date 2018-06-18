import debounce from 'lodash.debounce'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../../reducers/data'
import {
  getFormCollection,
  mergeForm,
  removeForm
} from '../../reducers/form'
import {
  AND,
  NEW,
  SEARCH
} from '../../utils/config'

class FormSearch extends Component {
  constructor(props) {
    super(props)
    this.state = {
      localValue: null
    }
    this.onDebouncedRequestDataSearch = debounce(
      this.onRequestDataSearch,
      props.debounceTimeout
    )
  }

  onChange = event => {
    event.persist()
    this.onDebouncedRequestDataSearch(event)
    this.setState({ localValue: event.target.value })
  }

  onItemClick = (event, found) => {
    const {
      collectionName,
      mergeForm
    } = this.props
    mergeForm(collectionName, SEARCH, found)
  }

  onResetFound = () => {
    const {
      collectionName,
      removeForm
    } = this.props
    removeForm(collectionName, SEARCH)
  }

  onRequestDataSearch = event => {
    const {
      target: { value },
    } = event
    const {
      collectionName,
      requestData,
    } = this.props
    //mergeForm(collectionName, entityId, name, mergedValue)
    const path = `search?collectionName=${collectionName}&q=${value.replace(/\s/g, AND)}`
    requestData('GET', path, { key: 'founds', isMergingArray: false })
  }

  handleSetDefaultValue () {
    // fill automatically the form when it is a NEW POST action
    const { defaultValue, entityId } = this.props
    defaultValue &&
      entityId === NEW &&
      this.onItemClick(null, defaultValue)
  }

  componentWillMount() {
    this.handleSetDefaultValue()
  }

  componentDidUpdate (prevProps) {
    if (this.props.defaultValue && !prevProps.defaultValue) {
      this.handleSetDefaultValue()
    }
  }

  render() {
    const {
      className,
      defaultValue,
      found,
      foundClassName,
      founds,
      id,
      ItemComponent,
      placeholder,
      autoComplete,
      required,
      type,
    } = this.props
    const {
      localValue
    } = this.state
    const foundValue = found || defaultValue
    return [
      foundValue
        ? <ItemComponent
          key={-2}
          onItemClick={this.onResetFound}
          {...foundValue}
        />
        : <input
            required={required}
            autoComplete={autoComplete}
            className={className || 'input'}
            id={id}
            key={-1}
            onChange={this.onChange}
            placeholder={placeholder}
            type={type}
            value={localValue || ''}
          />,
      !found && founds && <div className={foundClassName || 'box'} key={1}>
        {
          founds.map((found, index) => (
            <ItemComponent
              key={index}
              onItemClick={e => this.onItemClick(e, found, index)}
              {...found}
            />
          ))
        }
      </div>
    ]
  }
}

FormSearch.defaultProps = {
  debounceTimeout: 500,
  entityId: NEW,
}

export default connect(
  (state, ownProps) => ({
    founds: state.data.founds,
    found: (getFormCollection(state, ownProps) || {})[SEARCH]
  }),
  { mergeForm, removeForm, requestData }
)(FormSearch)
