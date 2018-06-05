import PropTypes from 'prop-types'
import debounce from 'lodash.debounce'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../../reducers/data'
import { closeLoading, showLoading } from '../../reducers/loading'
import { AND } from '../../utils/config'

class SearchInput extends Component {
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
    const {
      collectionNames,
      config,
      hook,
      onChange,
      requestData,
      showLoading
    } = this.props
    showLoading('search')
    const path = `search?collectionNames=${collectionNames.join(AND)}&q=${value}`
    requestData('GET', path, config)
    this._isDebouncing = false
    onChange && onChange(event)
  }

  onChange = event => {
    event.persist()
    //!this._isDebouncing && this.props.showLoading()
    this._isDebouncing = true
    this.onDebouncedRequestData(event)
  }

  render() {
    return <input
      className="input"
      onChange={this.onChange}
      placeholder="Saisissez une recherche"
      ref={_element => (this._element = _element)}
      type="text"
    />
  }
}

SearchInput.defaultProps = {
  debounceTimeout: 1000,
}

SearchInput.propTypes = {
  collectionNames: PropTypes.array.isRequired
}

export default connect(
  null,
  { closeLoading, requestData, showLoading }
)(SearchInput)
