import get from 'lodash.get'
import moment from 'moment'
import { requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import { mergeForm } from '../reducers/form'
import eventSelector from '../selectors/event'
import offerSelector from '../selectors/offer'
import timezoneSelector from '../selectors/timezone'
import venueSelector from '../selectors/venue'
import occasionSelector from '../selectors/occasion'
import occurencesSelector from '../selectors/occurences'
import { NEW } from '../utils/config'
import Form from './layout/Form'
import Field from './layout/Field'
import Submit from './layout/Submit'

import Icon from './layout/Icon'
import Price from './Price'

class OccurenceForm extends Component {

  handleSuccessData = (state, action) => {
    const {
      form,
      history,
      occasion,
      requestData,
      venue,
      tz
    } = this.props
    const {
      id
    } = (occasion || {})
    const {
      method,
      offerIdOrNew,
      storeKey
    } = this.state


    // ON A POST/PATCH EVENT OCCURENCE SUCCESS
    // WE CAN CHECK IF WE NEED TO POST/PATCH ALSO
    // AN ASSOCIATED OFFER
    const formOffer = get(form, `offersById.${offerIdOrNew}`) || {}
    if (storeKey !== 'offers' && method !== 'DELETE') {

      if (Object.keys(formOffer).length) {

        if (formOffer.bookingDate) {
          formOffer.bookingLimitDatetime = formOffer.bookingDate
            .tz(tz)
            .utc()
            .format()
        }

        const body = Object.assign({
          eventOccurenceId: action.data.id,
          offererId: venue.managingOffererId,
        }, formOffer)

        requestData(
          method,
          'offers',
          {
            body,
            key: 'offers'
          }
        )
      }
    }

    history.push(`/offres/${id}/dates`)

  }

  onDeleteClick = () => {
    const {
      occurence: {
        id,
      },
      offer,
      isFullyEditable,
      requestData,
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
            isFullyEditable && requestData(
              'DELETE',
              `eventOccurences/${id}`,
              {
                key: 'eventOccurences'
              }
            )
          }
        }
      )
    } else if (isFullyEditable) {
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
      isNew,
      isEditing,
      isFullyEditable,
      occasion,
      occurence,
      occurences,
      offer,
      tz,
    } = this.props

    const apiPath = isFullyEditable ? `eventOccurences/${get(occurence, 'id', '')}` : `offers/${get(offer, 'id', '')}`

    const formData = Object.assign({}, occasion, occurence, offer)

    return (
      <Form
        name={`occurence-${get(occurence, 'id', NEW)}`}
        TagName='tr'
        className='occurence-form'
        action={apiPath}
        handleSuccess={this.handleSuccessData}
        data={formData}
        layout='input-only'
        size="small"
        readOnly={!isEditing}
        method={isNew ? 'POST' : 'PATCH'}
      >
        <td>
          <Field type='date' name='beginningDate' dataKey='beginningDatetime' required highlightedDates={occurences.map(o => o.beginningDatetime)} title='Date' readOnly={!isFullyEditable} minDate='today' debug />
        </td>
        <td>
          <Field type='time' name='beginningTime' dataKey='beginningDatetime' required title='Heure' readOnly={!isFullyEditable} tz={tz} />
        </td>
        <td>
          <Field type='time' name='endDatetime' required title='Heure de fin' readOnly={!isFullyEditable} tz={tz} />
        </td>
        <td title='Vide si gratuit'>
          {isEditing ? <Field name="price" placeholder='Gratuit' title='Prix' /> : <Price value={get(offer, 'price')} /> }
        </td>
        <td title='Laissez vide si pas de limite'>
          <Field type='date' name='bookingLimitDatetime' maxDate={get(formData, 'beginningDatetime')} placeholder="Laissez vide si pas de limite" readOnly={!isFullyEditable}/>
        </td>
        <td title='Laissez vide si pas de limite'>
          <Field name='available' type='number' title='Places disponibles' />
        </td>
        <td>
          <Field type='hidden' name='eventId' />
          <Field type='hidden' name='venueId' />
          { isEditing ? (
            <NavLink
              to={`/offres/${get(occasion, 'id')}?dates`}
              className="button is-secondary is-small">Annuler</NavLink>
          ) : (
            <button
              className="button is-small is-secondary"
              onClick={this.onDeleteClick}>
              <span className='icon'><Icon svg='ico-close-r' /></span>
            </button>
          )}
        </td>
        <td>
          { isEditing ? (
            <Submit className="button is-primary is-small">Valider</Submit>
          ) : (
            <NavLink
              to={`/offres/${get(occasion, 'id')}?dates=${occurence.id}`}
              className="button is-small is-secondary">
              <span className='icon'><Icon svg='ico-pen-r' /></span>
            </NavLink>
          )}
        </td>
      </Form>
    )
  }
}

const newOccurenceWithDefaults = (occurence, offer) => {
  if (!occurence || !offer) return
  return {
    occurence: {
      beginningDatetime: moment(get(occurence, 'beginningDatetime')).add(1, 'day').toISOString(),
      endDatetime: moment(get(occurence, 'endDatetime')).add(1, 'day').toISOString(),
    },
    offer: {
      price: get(offer, 'price'),
      available: get(offer, 'available'),
      bookingLimitDatetime: moment(get(offer, 'bookingLimitDatetime')).add(1, 'day').toISOString(),
    },
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const occasion = occasionSelector(state, ownProps.match.params.occasionId)
      const { eventId, venueId } = (occasion || {})

      const occurence = get(ownProps, 'occurence')
      const offer = offerSelector(state, get(occurence, 'id'))
      const occurences = occurencesSelector(state, venueId, eventId)

      return Object.assign({
        event: eventSelector(state, eventId),
        venue: venueSelector(state, venueId),
        tz: timezoneSelector(state, venueId),
        occasion,
        occurences,
      }, ownProps.isNew ? newOccurenceWithDefaults(occurence, offer) : {
        occurence,
        offer,
      })
    },
    { mergeForm, requestData }
  )
)(OccurenceForm)
