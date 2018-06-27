import debounce from 'lodash.debounce'
import get from 'lodash.get'
import Icon from '../layout/Icon'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { assignData, requestData } from '../../reducers/data'
import { closeLoading, showLoading } from '../../reducers/loading'
import { AND } from '../../utils/config'

const KEY_RETURN = 13

class Search extends Component {
  constructor(props) {
    super(props)
    this.onDebouncedRequestData = debounce(
      this.onRequestData,
      props.debounceTimeout
    )
  }

  componentWillReceiveProps(nextProps) {
    const {
      closeLoading,
      offers
    } = nextProps
    if (offers !== this.props.offers) {
      closeLoading()
    }
  }
  
  onRequestData = event => {
    const {
      target: { value },
    } = event
    this.runSearch(value)
    this._isDebouncing = false
    this.onChange && this.onChange(event)
  }

  runSearch = value => {
    const {
      assignData,
      collectionName,
      config,
      onChange,
      requestData,
      showLoading
    } = this.props
    if (value.trim()) {
      // SEND A REQUEST WITH THIS QUERY
      showLoading('search')
      const path = `${collectionName}?search=${value}`
      requestData('GET', path, config)
    } else {
      // THE QUERY IS NULL
      // SO IT MEANS WE RESET THE SEARCH INPUT WITH AN EMPTY STRING
      // WE NEED THEN TO NULLIFY THE 'searched<Key>' in the state
      // to go back to the previous state without search
      const key = get(config, 'key')
      key && assignData({ [key]: null })
    }
  }

  onChange = event => {
    event.persist()
    //!this._isDebouncing && this.props.showLoading()
    this._isDebouncing = true
    this.onDebouncedRequestData(event)
  }

  render() {
    return (
          <div className="field is-grouped">
            <p className="control is-expanded">
              <input
                className="input search-input"
                //onChange={this.onChange}
                placeholder="Saisissez une recherche"
                ref={_element => (this._element = _element)}
                onKeyUp={e => e.keyCode == KEY_RETURN && this.runSearch(this._element.value)}
                type="text"
              />
            </p>
            <p className="control">
              <button  onClick={e => this.runSearch(this._element.value)} className='button is-primary is-outlined is-medium'>OK</button>
              {' '}
              <button className='button is-secondary is-medium'>&nbsp;<Icon svg='ico-filter' />&nbsp;</button>
            </p>
          </div>
      )
  }
}

Search.defaultProps = {
  debounceTimeout: 1000,
}

Search.propTypes = {
  collectionName: PropTypes.string.isRequired
}

export default connect(
  null,
  {
    assignData,
    closeLoading,
    showLoading,
    requestData
  }
)(Search)
