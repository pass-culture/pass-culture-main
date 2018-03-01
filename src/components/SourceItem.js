import React, { Component } from 'react'
import { connect } from 'react-redux'

import SourceModify from '../components/SourceModify'
import { requestData } from '../reducers/data'
import { showModal } from '../reducers/modal'

class SourceItem extends Component {
  onClick = () => {
    const { offererProviders, showModal } = this.props
    showModal(<SourceModify providers={offererProviders} />)
  }
  /*
  onToggle = () => {
    const { offererProviders,
      requestData
    } = this.props
    const body = offererProviders.map(({ id, isActive }) =>
      ({ id, isActive: !isActive }))
    requestData('PUT', `providers`, { body })
  }
  */
  render () {
    const { name, offererProviders } = this.props
    return (
      <div className='flex flex-start items-center mb1'>
        <input className='input--checkbox mr1'
          defaultChecked={offererProviders && offererProviders.length > 0}
          onClick={this.onToggle}
          type='checkbox' />
        <button className='mr2 button button--alive' onClick={this.onClick}>
          {name}
        </button>
      </div>
    )
  }
}

export default connect(null, { requestData, showModal })(SourceItem)
