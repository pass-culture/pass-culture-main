import React, { Component } from 'react'
import { connect } from 'react-redux'

import EditOffer from './EditOffer'
import WorkDetector from './WorkDetector'
import { assignForm } from '../reducers/form'
import { getCurrentWork } from '../reducers/request'

class NewOffer extends Component {
  componentWillReceiveProps (nextProps) {
    const { assignForm, work } = nextProps
    if (work && work !== this.props.work) {
      assignForm({ workId: work.id })
    }
  }
  render () {
    const { work } = this.props
    return (
      <div className='new-offer'>
        {
          work
            ? <EditOffer work={work} />
            : <WorkDetector />
        }
      </div>
    )
  }
}

export default connect(state => {
  return {
    selectedCategory: state.form && state.form.work && state.form.work.category,
    work: getCurrentWork(state)
  }
}, { assignForm })(NewOffer)
