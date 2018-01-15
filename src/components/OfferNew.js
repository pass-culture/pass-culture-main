import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import OfferModify from './OfferModify'
import WorkDetector from './WorkDetector'
import { mergeForm } from '../reducers/form'
import { NEW } from '../utils/config'

class OfferNew extends Component {
  componentWillReceiveProps (nextProps) {
    const { mergeForm, work } = nextProps
    if (work && work !== this.props.work) {
      const now = moment()
      const endDate = now.add(1, 'd').utc().format()
      const startDate = now.utc().format()
      mergeForm('offers', NEW, 'workId', work.id)
   }
  }
  render () {
    const { work } = this.props
    return (
      <div className='offer-new'>
        {
          work
            ? <OfferModify work={work} />
            : <WorkDetector />
        }
      </div>
    )
  }
}

export default connect(state => {
  return {
    work: state.data.works && state.data.works.length === 1 && state.data.works[0]
  }
}, { mergeForm })(OfferNew)
