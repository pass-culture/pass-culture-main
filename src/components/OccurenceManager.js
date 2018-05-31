import React, { Component } from 'react'
import { SingleDatePicker } from 'react-dates'
import { connect } from 'react-redux'
import moment from 'moment'

import Price from './Price'
import FormField from './layout/FormField'
import Label from './layout/Label'
import { mergeForm } from '../reducers/form'
import selectEventOccurences from '../selectors/eventOccurences'
import { DELETE } from '../utils/config'

class OccurenceManager extends Component {

  constructor() {
    super()
    this.state = {
      occurrences: [],
      calendarFocused: false,
      time: '',
      price: 0,
      groupSize: '',
      pmrGroupSize: '',
      withError: false,
    }
  }

  static defaultProps = {
    occurrences: [],
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    return {
      occurrences: nextProps.occurrences,
      withError: false,
    }
  }

  handleDateChange = date => {
    if (!this.state.time)
      return this.setState({ withError: true })
    const [hours, minutes] = this.state.time.split(':')
    const datetime = date.clone().hour(hours).minute(minutes)
    const isAlreadySelected = this.state.occurrences.find(o => o.datetime.isSame(datetime))
    this.props.onChange(
      this.state.occurrences
        .filter(o => isAlreadySelected ? !o.datetime.isSame(datetime) : true)
        .concat(isAlreadySelected ? [] : [{
          price: this.state.price,
          groupSize: this.state.groupSize,
          pmrGroupSize: this.state.pmrGroupSize,
          datetime,
        }])
        .sort((o1, o2) => o1.datetime.isBefore(o2.datetime) ? -1 : 1))
  }

  removeDate = ({ id }) => {
    this.props.mergeForm('eventOccurences', id, { DELETE, id })
  }

  render() {
    const occurences = this.state.occurences || this.props.occurences
    console.log('occurences', occurences)
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
                <td>{moment(o.beginningDatetime).format('DD/MM/YYYY')}</td>
                <td>{moment(o.beginningDatetime).format('HH:mm')}</td>
                <td><Price value={o.offer[0].price} /></td>
                <td>{o.offer[0].groupSize || 'Illimité'}</td>
                <td>{o.offer[0].pmrGroupSize || 'Illimité'}</td>
                <td>
                  <button className="delete is-small" onClick={e => this.removeDate(o)}/>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <SingleDatePicker
          calendarInfoPosition="top"
          renderCalendarInfo={() => (
            <div className='box content'>
              <p className={this.state.withError ? 'has-text-weight-bold has-text-danger' : ''}>Sélectionnez d'abord l'heure, le prix et le nombre de place disponibles puis cliquez sur les dates concernées :</p>
              <div className="field is-horizontal">
                <FormField
                  collectionName="eventOccurencesById"
                  label={<Label title="Heure" />}
                  name="time"
                  required
                  type="time"
                />
              </div>
              <div className="field is-horizontal">
                <FormField
                  collectionName="eventOccurencesById"
                  label={<Label title="Prix (€)" />}
                  min={0}
                  name="price"
                  required
                  type="number"
                />
              </div>
              <div className="field is-horizontal">
                <FormField
                  collectionName="eventOccurencesById"
                  label={<Label title="Nombre de places" />}
                  min={0}
                  name="groupSize"
                  placeholder="Laissez vide si pas de limite"
                  required
                  type="number"
                />
                <FormField
                  collectionName="eventOccurencesById"
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
          onFocusChange={e => this.setState({calendarFocused: !this.state.calendarFocused})}
          keepOpenOnDateSelect={true}
          isDayHighlighted={d1 => this.state.occurrences.some(d2 => d1.isSame(d2.datetime, 'day'))}
          placeholder='Ajouter un horaire'
        />
      </div>
    )
  }
}

export default connect(
  (state, ownProps) => ({
    isEditing: Object.keys(state.form) > 0,
    occurences: selectEventOccurences(state, ownProps)
  }),
  { mergeForm }
)(OccurenceManager)
