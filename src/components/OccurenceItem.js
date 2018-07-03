import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import OccurenceForm from './OccurenceForm'
import Price from './Price'
import Icon from './layout/Icon'
import { requestData } from '../reducers/data'
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
      offer,
      tz
    } = nextProps

    const {
      beginningDatetime,
      endDatetime,
      id
    } = (occurence || {})

    const {
      bookingLimitDatetime
    } = (offer || {})

    const date = beginningDatetime && moment.tz(beginningDatetime, tz)
    console.log('bookingLimitDatetime', bookingLimitDatetime)
    const bookingDate = bookingLimitDatetime && moment.tz(bookingLimitDatetime, tz)
    return {
      bookingDate: bookingDate && bookingDate.format('HH:mm'),
      date: date && date.format('DD/MM/YYYY'),
      endTime: endDatetime && moment.tz(endDatetime, tz).format('HH:mm'),
      isAdding: eventOccurenceId === 'nouvelle',
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
      offer,
      provider,
      requestData
    } = this.props
    const {
      id
    } = occurence

    // IF AN OFFER IS ASSOCIATED WE NEED TO DELETE IT FIRST
    if (offer) {
      requestData(
        'DELETE',
        `offers/${offer.id}`,
        {
          key: 'offers',
          handleSuccess: () => {
            !provider && requestData(
              'DELETE',
              `eventOccurences/${id}`,
              {
                key: 'eventOccurences'
              }
            )
          }
        }
      )
    } else if (!provider) {
      requestData(
        'DELETE',
        `eventOccurences/${id}`,
        {
          key: 'eventOccurences'
        }
      )
    }

  }

  render () {
    const {
      history,
      occasion,
      occurences,
      occurence,
      offer,
      provider,
      //tz
    } = this.props
    const {
      available,
      groupSize,
      pmrGroupSize,
      price
    } = (offer || {})

    const {
      bookingDate,
      date,
      endTime,
      isAdding,
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
        <td>{bookingDate || 'Pas de limite'}</td>
        <td>{available || 'Illimité'}</td>
        {false && (<td>{groupSize || 'Illimité'}</td>)}
        {false && (<td>{pmrGroupSize || 'Illimité'}</td>)}
        <td>
          {
            !provider && (
              <button
                className="button is-small is-secondary"
                onClick={this.onDeleteClick}
              >
                <span className='icon'><Icon svg='ico-close-r' /></span>
              </button>
            )
          }
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
