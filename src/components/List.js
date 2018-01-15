import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { assignData } from '../reducers/data'

import SubmitButton from './SubmitButton'

class List extends Component {
  constructor () {
    super()
    this.state = { isModify: null }
  }
  onAddClick = () => {
    this.setState({ isModify: true })
  }
  onSubmitClick = () => {
    const { assignData, name } = this.props
    assignData({ [name]: null })
    this.setState({ isModify: false })
  }
  render () {
    const { className,
      ContentComponent,
      elements,
      extra,
      FormComponent,
      getIsDisabled,
      isSubmitting,
      getBody,
      getOptimistState,
      path,
      title
    } = this.props
    const { isModify } = this.state
    return (
      <div className={className || 'list'} >
        <div className='h2 mb2'>
          {title}
        </div>
        <div className='list__control flex items-center flex-start'>
          {
            isModify
              ? <SubmitButton getBody={getBody}
                  getIsDisabled={getIsDisabled}
                  getOptimistState={getOptimistState}
                  onClick={this.onSubmitClick}
                  path={path}
                  text='Ajouter' />
              : (
                  <button className={classnames(
                      'button button--alive button--rounded left-align',
                      { 'hide': isSubmitting }
                    )}
                    onClick={this.onAddClick}>
                    +
                  </button>
              )
          }
        </div>
        { isModify && <FormComponent {...extra} /> }
        {
          elements && elements.map((favorite, index) => (
            <ContentComponent key={index} {...favorite} />
          ))
        }
      </div>
    )
  }
}

export default connect(
  (state, ownProps) => ({
    elements: state.data[ownProps.path] || ownProps.elements,
    isSubmitting: Object.keys(state.form).length > 0
  }),
  { assignData }
)(List)
