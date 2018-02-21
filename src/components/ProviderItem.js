import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../reducers/data'

class ProviderItem extends Component {
  onToggleClick = () => {
    const { ids, name } = this.props
    /*
    const offerProviders = offerProvider
      ? this.props.offerProviders.filter(_offerProvider => offerProvider != offerProvider)
      : this.props.offerProviders.concat(offerProvider)
    console.log('offerProviders', offerProviders)
    */
    const offerProviders = ids.map(id => `${name}:${id}`)
    // requestData('PUT', 'offerer', { body: { offerProviders } })
  }
  render () {
    const { ids, name } = this.props
    return (
      <div className='flex flex-start items-center mb1'>
        <input className='input--checkbox mr1'
          defaultChecked={ids.length > 0}
          onClick={this.onToggleClick}
          type='checkbox' />
        <div className='mr2'>
          {name}
        </div>
        {
          ids.map((id, index) => (
            <input className='input' key={index} value={id}/>
          ))
        }
      </div>
    )
  }
}

export default connect(null, { requestData })(ProviderItem)
