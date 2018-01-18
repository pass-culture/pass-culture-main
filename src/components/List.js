import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { assignData } from '../reducers/data'

import SubmitButton from './SubmitButton'

class List extends Component {
  onSubmitClick = () => {
    const { assignData, name } = this.props
    assignData({ [name]: null })
  }
  render () {
    const { className,
      ContentComponent,
      elements,
      extra,
      FormComponent,
      getIsDisabled,
      getBody,
      getOptimistState,
      isWrap,
      path,
      title
    } = this.props
    return (
      <div className={className || 'list'} >
        <div className='h2 mb2'>
          {title}
        </div>
        <div className='list__control flex items-center flex-start'>
          <SubmitButton
            getBody={getBody}
            getIsDisabled={getIsDisabled}
            getOptimistState={getOptimistState}
            onClick={this.onSubmitClick}
            path={path}
            text='Ajouter' />
        </div>
        <FormComponent {...extra} />
        <div className={classnames('list__content', {
          'flex items-center flex-wrap': isWrap
        })}>
          {
            elements && elements.map((favorite, index) => (
              <ContentComponent key={index} {...favorite} />
            ))
          }
        </div>
      </div>
    )
  }
}

export default connect(
  (state, ownProps) => ({
    elements: state.data[ownProps.path] || ownProps.elements
  }),
  { assignData }
)(List)
