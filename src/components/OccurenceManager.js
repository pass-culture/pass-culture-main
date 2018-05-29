import React, { Component } from 'react'
import { SingleDatePicker } from 'react-dates'
import { connect } from 'react-redux'
import moment from 'moment'

import Price from './Price'

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
      return this.setState({
      withError: true,
    })
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

  removeDate = occurrence => {
    this.props.onChange(this.state.occurrences
      .filter(o => !o.datetime.isSame(occurrence.datetime)))
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
                <div className="field-label is-normal">
                  <label className="label">Heure</label>
                </div>
                <div className="field-body">
                  <p>
                    <input required className='input' type='time' value={this.state.time} onChange={e => this.setState({time: e.target.value})} />
                  </p>
                </div>
              </div>
              <div className="field is-horizontal">
                <div className="field-label is-normal">
                  <label className="label">Prix</label>
                </div>
                <div className="field-body">
                  <p className="control has-icons-right">
                    <input className="input" type="number" placeholder="Prix" min={0} name='price' value={this.state.price} onChange={e => this.setState({price: e.target.value})} />
                    <span className="icon is-small is-right">
                      €
                    </span>
                  </p>
                </div>
              </div>
              <div className="field is-horizontal">
                <div className="field-label is-normal">
                  <label className="label">Nombre de places</label>
                </div>
                <div className="field-body">
                  <p className='field'>
                    <input placeholder='Laissez vide si pas de limite' className='input' type='number' min={0} name='groupSize' value={this.state.groupSize} onChange={e => this.setState({groupSize: e.target.value})}  />
                  </p>
                  <p className='field'>
                    <input placeholder='Places en PMR' className='input' type='number' min={0} name='pmrGroupSize' value={this.state.pmrGroupSize} onChange={e => this.setState({pmrGroupSize: e.target.value})}  />
                  </p>
                </div>
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
  state => ({
    isEditing: Object.keys(state.form) > 0
  })
)(OccurenceManager)
