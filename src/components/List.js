import classnames from 'classnames'
import React from 'react'
import { connect } from 'react-redux'

import { assignData } from '../reducers/data'
import SubmitButton from './SubmitButton'

const List = ({
  className,
  ContentComponent,
  elements,
  extra,
  FormComponent,
  getIsDisabled,
  getBody,
  getOptimistState,
  getSuccessState,
  isWrap,
  path,
  title,
}) => {
  return (
    <div className={className || 'list'}>
      <div className="h2 mb2">{title}</div>
      <div className="list__control flex items-center flex-start">
        <SubmitButton
          getBody={getBody}
          getIsDisabled={getIsDisabled}
          getOptimistState={getOptimistState}
          getSuccessState={getSuccessState}
          onClick={this.onSubmitClick}
          path={path}
          text="Ajouter"
        />
      </div>
      <FormComponent {...extra} />
      <div
        className={classnames('list__content', {
          'flex items-center flex-wrap': isWrap,
        })}
      >
        {elements &&
          elements.map((favorite, index) => (
            <ContentComponent key={index} {...favorite} />
          ))}
      </div>
    </div>
  )
}

export default connect(
  (state, ownProps) => ({
    elements: state.data[ownProps.path] || ownProps.elements,
  }),
  { assignData }
)(List)
