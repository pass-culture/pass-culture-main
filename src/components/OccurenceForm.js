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
      '$submit': null,
      'isEventOccurenceStep': true
    }
  }

  handleEventOccurenceSuccessData = (state, action) => {
    this.setState({ isEventOccurenceStep: false })
  }

  handleOfferSuccessData = (state, action) => {
    const {
      history,
      occasion,
    } = this.props
    history.push(`/offres/${get(occasion, 'id')}?dates`)
    this.setState({ isEventOccurenceStep: true })
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

  handleDefaultDatetime () {
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

  componentDidMount () {
    this.setState({ $submit: this.$submit })
    this.handleDefaultDatetime()
  }

  componentDidUpdate (prevProps) {
    this.handleDefaultDatetime()

    // bind endDatetime to be 1hour after the just set beginningDatetime
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
    const { isEventOccurenceStep } = this.state

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
          readOnly={!isEventOccurenceStep || !isEditing}
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
              readOnly={!isEventOccurenceStep || !isFullyEditable}
              required
              title='Date'
              type='date' />
          </td>
          <td>
            <Field
              dataKey='beginningDatetime'
              name='beginningTime'
              readOnly={!isEventOccurenceStep || !isFullyEditable}
              required
              title='Heure'
              type='time'
              tz={tz} />
          </td>
          <td>
            <Field
              dataKey='endDatetime'
              name='endTime'
              readOnly={!isEventOccurenceStep || !isFullyEditable}
              required
              title='Heure de fin'
              type='time'
              tz={tz} />
          </td>
          {
            isEditing && isEventOccurenceStep && (
              <Portal node={this.state.$submit}>
                <SubmitButton className="button is-primary is-small">
                  Valider
                </SubmitButton>
              </Portal>
            )
          }
        </Form>
        <Form
          action={`/offer/${get(offer, 'id', '')}`}
          data={Object.assign({
            eventOccurenceId: get(occurence, 'id')
          }, offer)}
          handleSuccess={this.handleOfferSuccessData}
          layout='input-only'
          key={1}
          name={`offer${get(offer, 'id', '')}`}
          size="small"
          readOnly={isEventOccurenceStep || !isEditing}
          TagName={null} >

          <td title='Vide si gratuit'>

            <Field name='eventOccurenceId' type='hidden' />

            {
              isEditing
                ? <Field name="price" placeholder='Gratuit' title='Prix' />
                : <Price value={get(offer, 'price')} />
            }
          </td>
          <td title='Laissez vide si pas de limite'>
            <Field
              maxDate={beginningDatetime}
              name='bookingLimitDatetime'
              placeholder="Laissez vide si pas de limite"
              readOnly={isEventOccurenceStep || !isFullyEditable}
              type='date' />
          </td>
          <td title='Laissez vide si pas de limite'>
            <Field
              name='available'
              readOnly={isEventOccurenceStep || !isFullyEditable}
              title='Places disponibles'
              type='number' />
          </td>
          {
            isEditing && !isEventOccurenceStep && occurence && (
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
      const occurence = occurenceSelector(state, ownProps.occurence)
      return {
        event: eventSelector(state, eventId),
        eventId,
        formBeginningDatetime: get(
          state,
          `form.occurence${get(occurence, 'id', '')}.data.beginningDatetime`
        ),
        venue: venueSelector(state, venueId),
        occasion,
        occurence,
        occurences: occurencesSelector(state, venueId, eventId),
        offer: offerSelector(state, get(ownProps, 'occurence.id')),
        tz: timezoneSelector(state, venueId),
        venueId
      }
    },
    { mergeFormData, requestData }
  )
)(OccurenceForm)
