import get from 'lodash.get'
import moment from 'moment'
import { requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import Price from './Price'
import Icon from './layout/Icon'
import occasionSelector from '../selectors/occasion'
import offerSelector from '../selectors/offer'
import timezoneSelector from '../selectors/timezone'

class OccurenceItem extends Component {

  // constructor() {
  //   super()
  //   this.state = {
  //     date: null,
  //     endTime: null,
  //     isEditing: null,
  //     time: null
  //   }
  // }

  // static getDerivedStateFromProps (nextProps) {
  //   const {
  //     occurence,
  //     offer: {
  //       bookingLimitDatetime
  //     },
  //     tz
  //   } = nextProps

  //   const {
  //     beginningDatetime,
  //     endDatetime,
  //     id
  //   } = occurence || {}

  //   const eventOccurenceId = queryStringToObject(search).dates

  //   const date = beginningDatetime && moment.tz(beginningDatetime, tz)
  //   const bookingDate = bookingLimitDatetime && moment.tz(bookingLimitDatetime, tz)
  //   return {
  //     bookingDate: bookingDate && bookingDate.format('DD/MM/YYYY'),
  //     date: date && date.format('DD/MM/YYYY'),
  //     endTime: endDatetime && moment.tz(endDatetime, tz).format('HH:mm'),
  //     isEditing: eventOccurenceId === id,
  //     time: date && date.format('HH:mm'),
  //   }
  // }

  onDeleteClick = () => {
    const {
      occurence: {
        id,
      },
      offer,
      isEditable,
      requestData
    } = this.props

    // IF AN OFFER IS ASSOCIATED WE NEED TO DELETE IT FIRST
    // TODO: move this to backend
    if (offer) {
      requestData(
        'DELETE',
        `offers/${offer.id}`,
        {
          key: 'offers',
          handleSuccess: () => {
            isEditable && requestData(
              'DELETE',
              `eventOccurences/${id}`,
              {
                key: 'eventOccurences'
              }
            )
          }
        }
      )
    } else if (isEditable) {
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
      occasion,
      occurence,
      offer: {
        available,
        bookingLimitDatetime,
        price,
      },
      isEditable,
      tz,
    } = this.props

    const {
      beginningDatetime,
      endDatetime,
    } = occurence || {}

    const date = beginningDatetime && moment.tz(beginningDatetime, tz)

    return (
      <tr>
        <td>{date && date.format('DD/MM/YYYY')}</td>
        <td>{date && date.format('HH:mm')}</td>
        <td>{endDatetime && moment.tz(endDatetime, tz).format('HH:mm')}</td>
        <td><Price value={price} /></td>
        <td>{bookingLimitDatetime && moment.tz(bookingLimitDatetime, tz).format('DD/MM/YYYY')}</td>
        <td>{available}</td>
        <td>
          { isEditable && (
            <button
              className="button is-small is-secondary"
              onClick={this.onDeleteClick}
            >
              <span className='icon'><Icon svg='ico-close-r' /></span>
            </button>
          )}
        </td>
        <td>
          <NavLink
            to={`/offres/${get(occasion, 'id')}?dates=${occurence.id}`}
            className="button is-small is-secondary">
            <span className='icon'><Icon svg='ico-pen-r' /></span>
          </NavLink>
        </td>
      </tr>
    )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const occasion = occasionSelector(state, ownProps.match.params.occasionId)
      const { venueId } = (occasion || {})
      return {
        occasion,
        offer: offerSelector(state, get(ownProps, 'occurence.id')),
        tz: timezoneSelector(state, 'venueId')
      }
    },
    { requestData }
  )
)(OccurenceItem)
