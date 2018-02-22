import debounce from 'lodash.debounce'
import React, { Component } from 'react'
import { Portal } from 'react-portal'
import { connect } from 'react-redux'

import Loading from './Loading'
import { requestData } from '../reducers/data'
import { closeLoading, showLoading } from '../reducers/loading'

class SearchInput extends Component {
  constructor (props) {
    super (props)
    this.handleDebouncedRequestData = debounce(
      this.handleRequestData,
      props.debounceTimeout
    )
  }
  componentWillReceiveProps (nextProps) {
    const { closeLoading, offers } = nextProps
    if (offers !== this.props.offers) {
      closeLoading()
    }
  }
  handleRequestData = event => {
    const { target: { value } } = event
    const { requestData } = this.props
    requestData('GET', `offers?search=${value}`)
    this._isDebouncing = false
  }
  onChange = event => {
    event.persist()
    !this._isDebouncing && this.props.showLoading()
    this._isDebouncing = true
    this.handleDebouncedRequestData(event)
  }
  render () {
    const children = [
      <input className='input search-input mx-auto col-9'
        key={0}
        onChange={this.onChange}
        placeholder='tape ta recherche'
        type='text' />
    ]
    window.location.pathname.includes('/gestion') && children.push(
      <Portal key={1}
        node={document && document.getElementById('header__content')}>
        <Loading />
      </Portal>
    )
    return children
  }
}

SearchInput.defaultProps = {
  debounceTimeout: 1000
}

export default connect(
  state => ({ offers: state.data.offers }),
  { closeLoading, requestData, showLoading }
)(SearchInput)
