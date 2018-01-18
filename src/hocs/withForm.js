import React, { Component } from 'react'
import { connect } from 'react-redux'

const withForm = WrappedComponent {
  const _withForm extends Component {
    componentWillMount () {
      this.handleMergeForm (this.props)
    }
    componentWillReceiveProps (nextProps) {
      if (nextProps.id !== this.props.id) {
        this.handleMergeForm(nextProps)
      }
    }
    handleMergeForm = props => {
      const { collectionName, id, mergeForm } = props
      id && mergeForm(collectionName, NEW, 'id', id)
    }
    render () {
      return <WrappedComponent {...this.props} />
    }
  }

  return connect(null, { mergeForm })(_withForm)
}
