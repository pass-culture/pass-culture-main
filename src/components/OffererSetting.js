import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import withSelectors from '../hocs/withSelectors'

class OffererSetting extends Component {
  render () {
    const { providers } = this.props
    console.log('providers', providers)
    return (
      <div className='offer-setting'>
        <div className='h2 mb1'>
          Mes sources
        </div>
        <div className='p3' >
        {
          providers && providers.map(({ isChecked, name }, index) => (
            <div className='flex flex-start items-center mb1' key={index}>
              <input className='input--checkbox mr1'
                defaultChecked={isChecked}
                type='checkbox' />
              <div>
                {name}
              </div>
            </div>
          ))
        }
        </div>
      </div>
    )
  }
}

export default compose(
  connect(
    state => Object.assign({
      providers: state.data.providers
    }, state.user && state.user.offerer)
  ),
  withSelectors({
    providers: [
      ownProps => ownProps.providers,
      ownProps => ownProps.offerProviders,
      (providers, offerProviders) => {
        const offerProviderIds = offerProviders.map(offerProvider => offerProvider.split(':')[0])
        return providers.map(({ id, name }) => ({
          name,
          isChecked: offerProviderIds.includes(id)
        }))
      }
    ]
  })
)(OffererSetting)
