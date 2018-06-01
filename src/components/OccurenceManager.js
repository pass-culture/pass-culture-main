import React, { Component } from 'react'
import { SingleDatePicker } from 'react-dates'
import { connect } from 'react-redux'
import moment from 'moment'

import Price from './Price'
import FormField from './layout/FormField'
import Label from './layout/Label'
import { mergeForm } from '../reducers/form'
import selectEventOccurences from '../selectors/eventOccurences'
import { DELETE, NEW } from '../utils/config'

class OccurenceManager extends Component {
  constructor () {
    super()
    this.state = {
      calendarFocused: false
    }
  }

  handleDateChange = date => {
    const {
      mergeForm,
      newDate,
      newOffer,
      occurences
    } = this.props

    // build the datetime based on the date plus the time
    // given in the horaire form field
    if (!newDate || !newDate.time || !newOffer) {
      return this.setState({ withError: true })
    }
    const [hours, minutes] = newDate.time.split(':')
    const datetime = date.clone().hour(hours).minute(minutes)

    // check that it does not match already an occurence
    const alreadySelectedOccurence = occurences.find(o =>
      o.beginningDatetimeMoment.isSame(datetime))
    if (alreadySelectedOccurence) {
      return
    }

    // add in the occurences form
    const eventOccurenceId = !occurences
      ? `NEW_0`
      : `${NEW}_${occurences.length}`
    mergeForm('eventOccurences', eventOccurenceId, {
      beginningDatetime: datetime,
      id: eventOccurenceId,
      // TODO: SHOULD BE FIXED WITH SOON API NEW MERGE
      offer: [newOffer]
    })
  }

  removeDate = ({ id }) => {
    this.props.mergeForm('eventOccurences', id, { DELETE, id })
  }

  render() {
    const { occurences } = this.props
    return (
      <div>
        <table className='table is-striped is-hoverable'>
          <thead>
            <tr>
              <td>Date</td>
              <td>Heure</td>
              <td>Prix</td>
              <td>Nombre de place total</td>
              <td>Nombre de place Personnes à Mobilité Réduite (PMR)</td>
              <td></td>
            </tr>
          </thead>
          <tbody>
            {occurences && occurences.map((o, index) => (
              <tr key={index} className=''>
                <td>{o.beginningDatetimeMoment.format('DD/MM/YYYY')}</td>
                <td>{o.beginningDatetimeMoment.format('HH:mm')}</td>
                <td><Price value={o.offer[0].price} /></td>
                <td>{o.offer[0].groupSize || 'Illimité'}</td>
                <td>{o.offer[0].pmrGroupSize || 'Illimité'}</td>
                <td>
                  <button
                    className="delete is-small"
                    onClick={e => this.removeDate(o)}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <SingleDatePicker
          calendarInfoPosition="top"
          renderCalendarInfo={() => (
            <div className='box content'>
              <p className={
                this.state.withError
                ? 'has-text-weight-bold has-text-danger'
                : ''
              }>
                Sélectionnez d'abord l'heure, le prix et le nombre de place disponibles puis cliquez sur les dates concernées :
              </p>
              <div className="field is-horizontal">
                <FormField
                  collectionName="dates"
                  label={<Label title="Heure" />}
                  name="time"
                  required
                  type="time"
                />
              </div>
              <div className="field is-horizontal">
                <FormField
                  collectionName="offers"
                  label={<Label title="Prix (€)" />}
                  min={0}
                  name="price"
                  required
                  type="number"
                />
              </div>
              <div className="field is-horizontal">
                <FormField
                  collectionName="offers"
                  label={<Label title="Nombre de places" />}
                  min={0}
                  name="groupSize"
                  placeholder="Laissez vide si pas de limite"
                  required
                  type="number"
                />
                <FormField
                  collectionName="offers"
                  label={<Label title="Places en PMR" />}
                  min={0}
                  name="pmrGroupSize"
                  placeholder="Laissez vide si pas de limite"
                  required
                  type="number"
                />
              </div>
            </div>
          )}
          onDateChange={this.handleDateChange}
          focused={this.state.calendarFocused}
          onFocusChange={e => this.setState({
              calendarFocused: !this.state.calendarFocused
            })
          }
          keepOpenOnDateSelect={true}
          isDayHighlighted={d1 =>
            occurences && occurences.some(o =>
              d1.isSame(o.beginningDatetimeMoment, 'day'))}
          placeholder='Ajouter un horaire'
        />
      </div>
    )
  }
}

export default connect(
  (state, ownProps) => ({
    newDate: state.form.datesById && state.form.datesById[NEW],
    newOffer: state.form.offersById && state.form.offersById[NEW],
    occurences: selectEventOccurences(state, ownProps)
  }),
  { mergeForm }
)(OccurenceManager)
