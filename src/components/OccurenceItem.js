import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import OccurenceForm from './OccurenceForm'
import Price from './Price'
import Icon from './layout/Icon'
import { requestData } from '../reducers/data'
import createEventSelector from '../selectors/createEvent'
import createOfferSelector from '../selectors/createOffer'
import createTimezoneSelector from '../selectors/createTimezone'
import createVenueSelector from '../selectors/createVenue'

class OccurenceItem extends Component {

  constructor() {
    super()
    this.state = {
      date: null,
      endTime: null,
      isEditing: null,
      time: null
    }
  }

  static getDerivedStateFromProps (nextProps) {
    const {
      match: { params: { eventOccurenceId } },
      occurence,
      tz
    } = nextProps

    const {
      beginningDatetime,
      endDatetime,
      id
    } = (occurence || {})

    const date = beginningDatetime && moment.tz(beginningDatetime, tz)
    return {
      date: date && date.format('DD/MM/YYYY'),
      endTime: endDatetime && moment.tz(endDatetime, tz).format('HH:mm'),
      isEditing: eventOccurenceId === id,
      time: date && date.format('HH:mm'),
    }
  }

  onEditClick = () => {
    const {
      history,
      location: { search },
      occasion,
      occurence
    } = this.props
    const {
      id
    } = (occasion || {})
    history.push(`/offres/${id}/dates/${occurence.id}${search}`)
  }

  onDeleteClick = () => {
    const {
      occurence,
      requestData
    } = this.props
    const {
      id
    } = occurence
    requestData(
      'DELETE',
      `eventOccurences/${id}`,
      {
        key: 'eventOccurences'
      }
    )
  }

  render () {
    const {
      history,
      isAdding,
      occasion,
      occurences,
      occurence,
      offer,
      tz
    } = this.props
    const {
      beginningDatetimeMoment,
      endDatetimeMoment
    } = (occurence || {})
    const {
      available,
      groupSize,
      pmrGroupSize,
      price
    } = (offer || {})

    const {
      date,
      endTime,
      isEditing,
      time,
    } = this.state

    if (isEditing) {
      return <OccurenceForm
        history={history}
        occasion={occasion}
        occurence={occurence}
        occurences={occurences}
        onDeleteClick={e => this.setState({isEditing: false})}
      />
    }
    return (
      <tr className=''>
        <td>{date}</td>
        <td>{time}</td>
        <td>{endTime}</td>
        <td><Price value={price || 0} /></td>
        <td>{available || 'Illimité'}</td>
        <td>{pmrGroupSize || 'Illimité'}</td>
        <td>
          <button
            className="button is-small is-secondary"
            onClick={this.onDeleteClick}
          >
            <span className='icon'><Icon svg='ico-close-r' /></span>
          </button>
        </td>
        <td>
          {
            (!isAdding || !isEditing) && (
              <button
                className="button is-small is-secondary"
                onClick={this.onEditClick}>
                <span className='icon'><Icon svg='ico-pen-r' /></span>
              </button>
            )
          }
        </td>
      </tr>
    )
  }
}

const venueSelector = createVenueSelector()
const timezoneSelector = createTimezoneSelector(venueSelector)


export default connect(
  () => {
    const offerSelector = createOfferSelector()
    return (state, ownProps) => ({
      offer: offerSelector(state, get(ownProps, 'occurence.id')),
      tz: timezoneSelector(state, get(ownProps, 'occasion.venueId'))
    })
  },
  { requestData }
)(OccurenceItem)
