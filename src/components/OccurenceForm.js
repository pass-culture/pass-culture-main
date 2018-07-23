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

  handleEventOccurenceSuccessData = (state, action) => {
    const {
      history,
      occasion,
      offer
    } = this.props
    const offerIdOrNew = get(offer, 'id', 'nouveau')
    history.push(`/offres/${get(occasion, 'id')}?gestion&date=${action.data.id}&stock=${offerIdOrNew}`)
  }

  handleOfferSuccessData = (state, action) => {
    const {
      history,
      occasion,
    } = this.props
    history.push(`/offres/${get(occasion, 'id')}?gestion`)
  }

  onDeleteClick = () => {
    const {
      occurence,
      offer,
      isFullyEditable,
      requestData,
    } = this.props

    // IF AN OFFER IS ASSOCIATED WE NEED TO DELETE IT FIRST
    if (offer) {
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

  handleNextDatetimes = () => {
    const {
      formBeginningDatetime,
      mergeFormData,
      occurence,
      occurences
    } = this.props
    // add automatically a default beginninDatetime and a endDatetime
    // one day after the previous occurence
    if (occurence) {
      return
    }
    if (!formBeginningDatetime && get(occurences, 'length')) {
      const beginningDatetime = moment(occurences[0].beginningDatetime).add(1, 'day')
      mergeFormData('occurence', {
        beginningDatetime,
        endDatetime: moment(beginningDatetime).add(1, 'hour')
      })
      return
    }
  }

  handleCrossingEndDatetime = () => {
    const {
      formBeginningDatetime,
      formEndDatetime,
      mergeFormData
    } = this.props
    if (formEndDatetime < formBeginningDatetime) {
      mergeFormData('occurence', {
        endDatetime: moment(formEndDatetime).add(1, 'day')
      })
    }
  }

  handleInitEndDatetime = (prevProps) => {
    const {
      formBeginningDatetime,
      mergeFormData,
      occurence,
    } = this.props
    if (occurence) {
      return
    }
    if (formBeginningDatetime !== prevProps.formBeginningDatetime) {
      mergeFormData('occurence', {
        endDatetime: moment(formBeginningDatetime).add(1, 'hour')
      })
    }
  }

  componentDidMount () {
    this.setState({ $submit: this.$submit })
    this.handleNextDatetimes()
  }

  componentDidUpdate (prevProps) {
    this.handleNextDatetimes()
    this.handleCrossingEndDatetime()
    this.handleInitEndDatetime(prevProps)
  }

  render () {

    const {
      eventId,
      eventOccurenceIdOrNew,
      formBeginningDatetime,
      isEventOccurenceReadOnly,
      isFullyEditable,
      isNew,
      occasion,
      occurence,
      occurences,
      offer,
      offerIdOrNew,
      tz,
      venueId
    } = this.props

    const beginningDatetime = formBeginningDatetime ||
      get(occurence, 'beginningDatetime')

    return (
      <tr className='occurence-form'>
        <Form
          action={`/eventOccurences/${get(occurence, 'id', '')}`}
          data={Object.assign({}, occurence, {
            eventId,
            venueId
          })}
          handleSuccess={this.handleEventOccurenceSuccessData}
          layout='input-only'
          name={`occurence${get(occurence, 'id', '')}`}
          readOnly={!eventOccurenceIdOrNew || offerIdOrNew}
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
              dataKey='beginningDatetime'
              debug
              highlightedDates={occurences.map(o => o.beginningDatetime)}
              minDate='today'
              name='beginningDate'
              readOnly={isEventOccurenceReadOnly}
              required
              title='Date'
              type='date' />
          </td>
          <td>
            <Field
              dataKey='beginningDatetime'
              name='beginningTime'
              readOnly={isEventOccurenceReadOnly}
              required
              title='Heure'
              type='time'
              tz={tz} />
          </td>
          <td>
            <Field
              dataKey='endDatetime'
              name='endTime'
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
          data={Object.assign({
            eventOccurenceIdOrNew: get(occurence, 'id')
          }, offer)}
          handleSuccess={this.handleOfferSuccessData}
          layout='input-only'
          key={1}
          name={`offer${get(offer, 'id', '')}`}
          size="small"
          readOnly={!offerIdOrNew}
          TagName={null} >

          <td title='Vide si gratuit'>

            <Field name='eventOccurenceIdOrNew' type='hidden' />

            {
              offerIdOrNew
                ? <Field
                    name="price"
                    placeholder='Gratuit'
                    title='Prix'  />
                : <Price value={get(offer, 'price')} />
            }

          </td>
          <td title='Laissez vide si pas de limite'>
            <Field
              maxDate={beginningDatetime}
              name='bookingLimitDatetime'
              placeholder="Laissez vide si pas de limite"
              readOnly={!offerIdOrNew}
              type='date' />
          </td>
          <td title='Laissez vide si pas de limite'>
            <Field
              name='available'
              readOnly={!offerIdOrNew}
              title='Places disponibles'
              type='number' />
          </td>
          {
            isEventOccurenceReadOnly && occurence && (
              <Portal node={this.state.$submit}>
                <SubmitButton className="button is-primary is-small">
                  Valideeeer
                </SubmitButton>
              </Portal>
            )
          }
        </Form>
        <td>
          {
            (eventOccurenceIdOrNew || offerIdOrNew)
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
            !eventOccurenceIdOrNew && !offerIdOrNew && (
              <NavLink
                to={`/offres/${get(occasion, 'id')}?gestion&date=${occurence.id}`}
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

      const isEventOccurenceReadOnly = !eventOccurenceIdOrNew ||
        offerIdOrNew ||
        !ownProps.isFullyEditable

      const occasion = occasionSelector(state, ownProps.match.params.occasionId)
      const { eventId, venueId } = (occasion || {})
      const occurence = occurenceSelector(state, ownProps.occurence)

      return {
        event: eventSelector(state, eventId),
        eventId,
        eventOccurenceIdOrNew,
        formBeginningDatetime: get(
          state,
          `form.occurence${get(occurence, 'id', '')}.data.beginningDatetime`
        ),
        formEndDatetime: get(
          state,
          `form.occurence${get(occurence, 'id', '')}.data.endDatetime`
        ),
        isEventOccurenceReadOnly,
        occasion,
        occurence,
        offerIdOrNew,
        occurences: occurencesSelector(state, venueId, eventId),
        offer: offerSelector(state, get(ownProps, 'occurence.id')),
        tz: timezoneSelector(state, venueId),
        venue: venueSelector(state, venueId),
        venueId
      }
    },
    { mergeFormData, requestData }
  )
)(OccurenceForm)
