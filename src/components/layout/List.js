import classnames from 'classnames'
import React from 'react'
import { connect } from 'react-redux'

import SubmitButton from './SubmitButton'
import { assignData } from '../../reducers/data'

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
      <h2 className="title is-2">{title}</h2>
      <div className="control">
        <SubmitButton
          className="button is-primary"
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
        className={classnames('content', {
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
