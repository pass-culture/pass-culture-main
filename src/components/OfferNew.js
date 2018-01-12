import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import OfferModify from './OfferModify'
import WorkDetector from './WorkDetector'
import { assignForm } from '../reducers/form'

class OfferNew extends Component {
  componentWillReceiveProps (nextProps) {
    const { assignForm, work } = nextProps
    if (work && work !== this.props.work) {
      const now = moment()
      const endDate = now.add(1, 'd').utc().format()
      const startDate = now.utc().format()
      assignForm({
        prices: [
          {
            endDate,
            size: 1,
            startDate,
            value: 10
          }
        ],
        workId: work.id
      })
    }
  }
  render () {
    const { prices, sellersFavorites, work } = this.props
    return (
      <div className='offer-new'>
        {
          work
            ? <OfferModify prices={prices}
                sellersFavorites={sellersFavorites}
                work={work}
              />
            : <WorkDetector />
        }
      </div>
    )
  }
}

export default connect(state => {
  return {
    prices: state.form && state.form.prices,
    sellersFavorites: state.form.sellersFavorites,
    selectedCategory: state.form && state.form.work && state.form.work.category,
    work: state.data.works && state.data.works.length === 1 && state.data.works[0]
  }
}, { assignForm })(OfferNew)
