import get from 'lodash.get'
import {
  Field,
  Form,
  Icon,
  mergeForm,
  requestData,
  resetForm,
  SubmitButton
} from 'pass-culture-shared'
import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Portal } from 'react-portal'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import eventSelector from '../selectors/event'
import searchSelector from '../selectors/search'
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

  onDeleteClick = () => {
    const {
      occurence,
      offer,
      isFullyEditable,
      requestData,
    } = this.props

    // IF AN OFFER IS ASSOCIATED WE NEED TO DELETE IT FIRST
    if (get(offer, 'id')) {
      requestData(
        'DELETE',
        `offers/${offer.id}`,
        {
          key: 'offers',
          handleSuccess: () => {
            isFullyEditable && requestData(
              'DELETE',
              `eventOccurences/${occurence.id}`,
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
        `eventOccurences/${occurence.id}`,
        {
          key: 'eventOccurences'
        }
      )
    }
  }

  handleCrossingEndDatetime = () => {
    const {
      formBeginningDatetime,
      formEndDatetime,
      mergeForm
    } = this.props
    if (formEndDatetime < formBeginningDatetime) {
      mergeForm('occurence', {
        endDatetime: moment(formEndDatetime)
                      .add(1, 'day')
                      .toISOString()
      })
    }
  }

  handleEventOccurenceSuccessData = (state, action) => {
    const {
      history,
      occasion,
      offer
    } = this.props
    const offerIdOrNew = get(offer, 'id', 'nouveau')
    history.push(`/offres/${get(occasion, 'id')}?gestion&date=${action.data.id}&stock=${offerIdOrNew}`)
  }

  handleInitBookingLimitDatetime = () => {
    const {
      formBookingLimitDatetime,
      isOfferReadOnly,
      mergeForm,
      occurence
    } = this.props
    if (!get(occurence, 'id') || formBookingLimitDatetime || isOfferReadOnly) {
      return
    }

    mergeForm('offer', {
      bookingLimitDatetime: moment(occurence.beginningDatetime)
                              .subtract(2, 'day')
                              .toISOString()
    })
  }

  handleInitEndDatetime = () => {
    const {
      formBeginningDatetime,
      mergeForm,
      occurence,
    } = this.props
    if (get(occurence, 'id')) {
      return
    }
    mergeForm('occurence', {
      endDatetime: moment(formBeginningDatetime)
                    .add(1, 'hour')
                    .toISOString()

    })
  }

  handleInitPrice = () => {
    const {
      formPrice,
      mergeForm,
      offer,
    } = this.props
    if (get(offer, 'id') || formPrice) {
      return
    }
    mergeForm('offer', { price: 0 })
  }

  handleNextDatetimes = () => {
    const {
      formBeginningDatetime,
      mergeForm,
      occurence,
      occurences
    } = this.props
    // add automatically a default beginninDatetime and a endDatetime
    // one day after the previous occurence
    if (get(occurence, 'id')) {
      return
    }
    if (!formBeginningDatetime && get(occurences, 'length')) {
      const beginningDatetime = moment(occurences[0].beginningDatetime).add(1, 'day')
      mergeForm('occurence', {
        beginningDatetime,
        endDatetime: moment(beginningDatetime).add(1, 'hour')
      })
    }
  }

  handleOfferSuccessData = (state, action) => {
    const {
      history,
      occasion,
    } = this.props
    history.push(`/offres/${get(occasion, 'id')}?gestion`)
  }

  handleResetForm = () => {
    const {
      isEditing,
      resetForm
    } = this.props
    if (!isEditing) {
      resetForm()
    }
  }

  componentWillMount() {
    this.handleResetForm()
  }

  componentDidMount () {
    this.setState({ $submit: this.$submit })
    this.handleNextDatetimes()
    this.handleInitBookingLimitDatetime()
    this.handleInitPrice()
  }

  componentDidUpdate (prevProps) {
    const {
      formBeginningDatetime,
      isEditing
    } = this.props

    if (prevProps.isEditing && !isEditing) {
      this.handleResetForm()
    }

    this.handleNextDatetimes()
    this.handleInitBookingLimitDatetime()
    this.handleCrossingEndDatetime()

    if (formBeginningDatetime && !prevProps.formBeginningDatetime) {
      this.handleInitEndDatetime()
    }

    this.handleInitPrice()
  }

  render () {

    const {
      formBeginningDatetime,
      isEditing,
      isEventOccurenceReadOnly,
      isOfferReadOnly,
      occasion,
      occurence,
      occurences,
      offer,
      tz
    } = this.props

    const beginningDatetime = formBeginningDatetime ||
      get(occurence, 'beginningDatetime')

    return (
      <tr className='occurence-form'>
        <Form
          action={`/eventOccurences/${get(occurence, 'id', '')}`}
          handleSuccess={this.handleEventOccurenceSuccessData}
          layout='input-only'
          name={`occurence${get(occurence, 'id', '')}`}
          patch={occurence}
          readOnly={isEventOccurenceReadOnly}
          size="small"
          TagName={null} >
          <td>

            <Field name='eventId' type='hidden' />
            <Field name='venueId' type='hidden' />
            <Field
              minDate={beginningDatetime}
              name='endDatetime'
              type='hidden' />

            <Field
              debug
              highlightedDates={occurences.map(o => o.beginningDatetime)}
              minDate='today'
              name='beginningDate'
              patchKey='beginningDatetime'
              readOnly={isEventOccurenceReadOnly}
              required
              title='Date'
              type='date' />
          </td>
          <td>
            <Field
              name='beginningTime'
              patchKey='beginningDatetime'
              readOnly={isEventOccurenceReadOnly}
              required
              title='Heure'
              type='time'
              tz={tz} />
          </td>
          <td>
            <Field
              name='endTime'
              patchKey='endDatetime'
              readOnly={isEventOccurenceReadOnly}
              required
              title='Heure de fin'
              type='time'
              tz={tz} />
          </td>
          {
            !isEventOccurenceReadOnly && (
              <Portal node={this.state.$submit}>
                <SubmitButton className="button is-primary is-small">
                  Valider
                </SubmitButton>
              </Portal>
            )
          }
        </Form>
        <Form
          action={`/offers/${get(offer, 'id', '')}`}
          handleSuccess={this.handleOfferSuccessData}
          layout='input-only'
          key={1}
          name={`offer${get(offer, 'id', '')}`}
          patch={offer}
          size="small"
          readOnly={isOfferReadOnly}
          TagName={null} >

          <td title='Vide si gratuit'>
            <Field name='eventOccurenceId' type='hidden' />
            <Field name='offererId' type='hidden' />
            <Field
              displayValue={(value, {readOnly}) => value === 0
                ? readOnly ? 'Gratuit' : 0
                : readOnly ? `${value}€` : value
              }
              name='price'
              placeholder='Gratuit'
              type='number'
              title='Prix' />
          </td>
          <td title='Laissez vide si pas de limite'>
            <Field
              maxDate={beginningDatetime}
              name='bookingLimitDatetime'
              placeholder="Laissez vide si pas de limite"
              type='date' />
          </td>
          <td title='Laissez vide si pas de limite'>
            <Field
              name='available'
              title='Places disponibles'
              type='number' />
          </td>
          {
            !isOfferReadOnly && (
              <Portal node={this.state.$submit}>
                <SubmitButton className="button is-primary is-small">
                  Valider
                </SubmitButton>
              </Portal>
            )
          }
        </Form>
        <td>
          {
            isEditing
              ? (
                  <NavLink
                    className="button is-secondary is-small"
                    to={`/offres/${get(occasion, 'id')}?gestion`}>
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
                to={`/offres/${get(occasion, 'id')}?gestion&date=${get(occurence, 'id')}`}
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

      const search = searchSelector(state, ownProps.location.search)
      const { eventOccurenceIdOrNew, offerIdOrNew } = (search || {})

      const occasion = occasionSelector(state, ownProps.match.params.occasionId)
      const { eventId, venueId } = (occasion || {})

      const occurence = occurenceSelector(state, ownProps.occurence, eventId, venueId)
      const occurenceId = get(occurence, 'id')

      const isEventOccurenceReadOnly = !eventOccurenceIdOrNew ||
        (eventOccurenceIdOrNew === 'nouvelle' && occurenceId) ||
        (
          eventOccurenceIdOrNew !== 'nouvelle' &&
          occurenceId !== eventOccurenceIdOrNew
        ) ||
        offerIdOrNew ||
        !ownProps.isFullyEditable

      const venue = venueSelector(state, venueId)

      const offer = offerSelector(state,
        get(ownProps, 'occurence.id'),
        get(venue, 'managingOffererId')
      )
      const offerId = get(offer, 'id')

      const isOfferReadOnly = !occurenceId ||
        !eventOccurenceIdOrNew ||
        eventOccurenceIdOrNew === "nouvelle" ||
        eventOccurenceIdOrNew !== occurenceId ||
        !offerIdOrNew ||
        (offerIdOrNew === 'nouveau' && offerId) ||
        (
          offerIdOrNew !== 'nouveau' &&
          offerId !== offerIdOrNew
        )

      const isEditing = !isEventOccurenceReadOnly || !isOfferReadOnly

      return {
        event: eventSelector(state, eventId),
        eventId,
        eventOccurenceIdOrNew,
        formBeginningDatetime: get(
          state,
          `form.occurence${occurenceId || ''}.beginningDatetime`
        ),
        formBookingLimitDatetime: get(
          state,
          `form.offer${offerId || ''}.bookingLimitDatetime`
        ),
        formEndDatetime: get(
          state,
          `form.occurence${occurenceId || ''}.endDatetime`
        ),
        formPrice: get(
          state,
          `form.offer${offerId || ''}.price`
        ),
        isEditing,
        isEventOccurenceReadOnly,
        isOfferReadOnly,
        occasion,
        occurence,
        offerIdOrNew,
        occurences: occurencesSelector(state, venueId, eventId),
        offer,
        tz: timezoneSelector(state, venueId),
        venue,
        venueId
      }
    },
    { mergeForm, requestData, resetForm }
  )
)(OccurenceForm)
