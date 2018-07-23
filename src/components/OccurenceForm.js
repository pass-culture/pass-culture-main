import get from 'lodash.get'
import moment from 'moment'
import { requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Portal } from 'react-portal'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import Price from './Price'
import Field from './layout/Field'
import Form from './layout/Form'
import Icon from './layout/Icon'
import SubmitButton from './layout/SubmitButton'
import { mergeFormData } from '../reducers/form'
import eventSelector from '../selectors/event'
import timezoneSelector from '../selectors/timezone'
import occasionSelector from '../selectors/occasion'
import occurenceSelector from '../selectors/occurence'
import occurencesSelector from '../selectors/occurences'
import offerSelector from '../selectors/offer'
import venueSelector from '../selectors/venue'


class OccurenceForm extends Component {

  constructor () {
    super()
    this.state = {
      '$submit': null
    }
  }

  handleSuccessData = (state, action) => {
    const {
      history,
      occasion,
    } = this.props

    /*
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
    */
    history.push(`/offres/${get(occasion, 'id')}/dates`)
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

  componentDidMount () {
    this.setState({ $submit: this.$submit })
  }

  componentDidUpdate (prevProps) {
    const {
      formBeginningDatetime,
      mergeFormData,
      occurences
    } = this.props

    // look if
    if (!formBeginningDatetime && get(occurences, 'length')) {
      console.log('ON POURRAIT', occurences)
      mergeFormData('occurence', {
        beginningDatetime: moment(occurences[0].beginningDatetime).add(1, 'day')
      })
      return
    }


    // bind endDatetime to be 1hour after the juste set already
    // beginningDatetime
    if (formBeginningDatetime !== prevProps.formBeginningDatetime) {
      mergeFormData('occurence', {
        endDatetime: moment(formBeginningDatetime).add(1, 'hour')
      })
    }
  }

  render () {

    const {
      eventId,
      isNew,
      isEditing,
      isFullyEditable,
      formBeginningDatetime,
      occasion,
      occurence,
      occurences,
      offer,
      tz,
      venueId
    } = this.props

    const maxDate = formBeginningDatetime ||
      get(occurence, 'beginningDatetime')

    return (
      <tr>
        <Form
          action={`/eventOccurences/${get(occurence, 'id', '')}`}
          className='occurence-form'
          data={Object.assign({}, occurence, {
            eventId,
            venueId
          })}
          handleSuccess={this.handleSuccessData}
          layout='input-only'
          name='occurence'
          readOnly={!isEditing}
          size="small"
          TagName={null}>
          <td>

            <Field name='eventId' type='hidden' />
            <Field name='venueId' type='hidden' />
            <Field
              maxDate={maxDate}
              name='endDatetime'
              type='hidden' />

            <Field
              dataKey='beginningDatetime'
              debug
              highlightedDates={occurences.map(o => o.beginningDatetime)}
              minDate='today'
              name='beginningDate'
              readOnly={!isFullyEditable}
              required
              title='Date'
              type='date' />
          </td>
          <td>
            <Field
              dataKey='beginningDatetime'
              name='beginningTime'
              readOnly={!isFullyEditable}
              required
              title='Heure'
              type='time'
              tz={tz} />
          </td>
          <td>
            <Field
              dataKey='endDatetime'
              name='endTime'
              readOnly={!isFullyEditable}
              required
              title='Heure de fin'
              type='time'
              tz={tz} />
          </td>
          {
            isEditing && (
              <Portal node={this.state.$submit}>
                <SubmitButton className="button is-primary is-small submitt">
                  Valider
                </SubmitButton>
              </Portal>
            )
          }
        </Form>
        <Form
          action={`/offer/${get(offer, 'id', '')}`}
          className='occurence-form'
          data={offer}
          handleSuccess={this.handleSuccessData}
          layout='input-only'
          key={1}
          name='offer'
          size="small"
          TagName={null}
          readOnly={!isEditing} >

          <td title='Vide si gratuit'>
            {
              isEditing
                ? <Field name="price" placeholder='Gratuit' title='Prix' />
                : <Price value={get(offer, 'price')} />
            }
          </td>
          <td title='Laissez vide si pas de limite'>
            <Field
              maxDate={maxDate}
              name='bookingLimitDatetime'
              placeholder="Laissez vide si pas de limite"
              readOnly={!isFullyEditable}
              type='date' />
          </td>
          <td title='Laissez vide si pas de limite'>
            <Field name='available' type='number' title='Places disponibles' />
          </td>
        </Form>
        <td>
          {
            isEditing
              ? (
                  <NavLink
                    className="button is-secondary is-small"
                    to={`/offres/${get(occasion, 'id')}?dates`}>
                    Annuler
                  </NavLink>
                )
              : (
                <button
                  className="button is-small is-secondary"
                  onClick={this.onDeleteClick}>
                  <span className='icon'><Icon svg='ico-close-r' /></span>
                </button>
              )
          }
        </td>
        <td ref={_e => this.$submit = _e}>
          {
            !isEditing && (
              <NavLink
                to={`/offres/${get(occasion, 'id')}?dates=${occurence.id}`}
                className="button is-small is-secondary">
                <span className='icon'><Icon svg='ico-pen-r' /></span>
              </NavLink>
            )
          }
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
      const { eventId, venueId } = (occasion || {})

      return {
        event: eventSelector(state, eventId),
        eventId,
        formBeginningDatetime: get(state, 'form.occurence.data.beginningDatetime'),
        // formEndDatetime: get(state, 'form.occurence.data.endDatetime'),
        venue: venueSelector(state, venueId),
        occasion,
        occurence: occurenceSelector(state, ownProps.occurence),
        occurences: occurencesSelector(state, venueId, eventId),
        offer: offerSelector(state, get(ownProps, 'occurence.id')),
        tz: timezoneSelector(state, venueId),
        venueId
      }
    },
    { mergeFormData, requestData }
  )
)(OccurenceForm)
