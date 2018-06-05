import PropTypes from 'prop-types'
import debounce from 'lodash.debounce'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../../reducers/data'
import { AND } from '../../utils/config'

const withSearch = WrappedComponent => {
  class _withSearch extends Component {
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

    onRequestDataSearch = event => {
      const {
        target: { value },
      } = event
      const {
        collectionNames,
        config,
        storeKey,
        requestData,
      } = this.props
      const path = `search?collectionNames=${collectionNames.join(AND)}&q=${value.replace(/\s/g, AND)}`
      requestData('GET', path, config)
    }

    render() {
      return <WrappedComponent {...this.props} onSearchChange={this.onChange}/>
    }
  }

  _withSearch.defaultProps = {
    debounceTimeout: 500
  }

  _withSearch.propTypes = {
    collectionNames: PropTypes.array.isRequired
  }

  return connect(null, { requestData })(_withSearch)
}
