import classnames from 'classnames'
import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import OfferModify from './OfferModify'
import ThingDetector from './ThingDetector'
import { mergeForm } from '../../reducers/form'
import { NEW } from '../../utils/config'

class OfferNew extends Component {
  componentWillReceiveProps(nextProps) {
    const { mergeForm, thing } = nextProps
    if (thing && thing !== this.props.thing) {
      const now = moment()
      const endDate = now
        .add(1, 'd')
        .utc()
        .format()
      const startDate = now.utc().format()
      mergeForm('prices', NEW, 'endDate', endDate)
      mergeForm('prices', NEW, 'startDate', startDate)
      mergeForm('offers', NEW, 'thingId', thing.id)
    }
  }
  render() {
    const { thing } = this.props
    return (
      <div
        className={classnames('offer-new', {
          'offer-new--thing-detector mt2 flex items-center': !thing,
        })}
      >
        {thing ? <OfferModify thing={thing} /> : <ThingDetector />}
      </div>
    )
  }
}

export default connect(
  state => ({ thing: state.data.things && state.data.things[0] }),
  { mergeForm }
)(OfferNew)
