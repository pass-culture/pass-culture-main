import React from 'react'
import { connect } from 'react-redux'

import SourceItem from './SourceItem'
import selectSources from '../selectors/sources'

const OffererForm = ({ sources }) => {
  return (
    <div className="offerer-form">
      <div className="h2 mb1">Mes sources</div>
      <div className="p3">
        {sources &&
          sources.map((source, index) => (
            <SourceItem key={index} {...source} />
          ))}
      </div>
    </div>
  )
}

export default connect(state =>
  Object.assign(
    { sources: selectSources(state) },
    state.user && state.user.offerer
  )
)(OffererForm)
