import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import SourceItem from './SourceItem'
import withSelectors from '../hocs/withSelectors'

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

export default compose(
  connect(state =>
    Object.assign(
      {
        offererProviders:
          state.data.offerers &&
          state.data.offerers[0] &&
          state.data.offerers[0].offererProviders,
        providers: state.data.providers,
      },
      state.user && state.user.offerer
    )
  ),
  withSelectors({
    sources: [
      ownProps => ownProps.providers,
      ownProps => ownProps.offererProviders,
      (providers, offererProviders) => {
        return providers.map(({ localClass, name }) => {
          return {
            offererProviders:
              offererProviders &&
              offererProviders.filter(
                offererProvider =>
                  offererProvider.provider.localClass === localClass
              ),
            name,
          }
        })
      },
    ],
  })
)(OffererForm)
