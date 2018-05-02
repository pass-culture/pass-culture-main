import React, { Component } from 'react'
import { connect } from 'react-redux'

import SourceModify from './SourceModify'
import { requestData } from '../reducers/data'
import { showModal } from '../reducers/modal'

class SourceItem extends Component {
  onClick = () => {
    const { offererProviders, showModal } = this.props
    showModal(<SourceModify providers={offererProviders} />)
  }
  render() {
    const { name, offererProviders } = this.props
    return (
      <div className="flex flex-start items-center mb1">
        <input
          className="input checkbox"
          defaultChecked={offererProviders && offererProviders.length > 0}
          onClick={this.onToggle}
          type="checkbox"
        />
        <button className="button is-default" onClick={this.onClick}>
          {name}
        </button>
      </div>
    )
  }
}

export default connect(null, { requestData, showModal })(SourceItem)
