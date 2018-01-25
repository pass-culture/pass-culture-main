import React, { Component } from 'react'
import { createSelector } from 'reselect'

const withSelectors = patch => WrappedComponent => {
  class _withSelectors extends Component {
    constructor () {
      super()
      this.state = {}
      Object.keys(patch)
        .forEach(key => {
          this[`${key}Selector`] = createSelector(...patch[key])
        })
    }
    componentWillMount () {
      this.handleSelectorsUpdate(this.props)
    }
    componentWillReceiveProps (nextProps) {
      this.handleSelectorsUpdate(nextProps)
    }
    handleSelectorsUpdate = props => {
      const nextState = {}
      Object.keys(patch)
        .forEach(key => {
          nextState[key] = this[`${key}Selector`](props)
        })
      this.setState(nextState)
    }
    render () {
      return <WrappedComponent {...this.props} {...this.state} />
    }
  }
  return _withSelectors
}

export default withSelectors
