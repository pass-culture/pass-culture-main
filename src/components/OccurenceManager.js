import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import OccurenceForm from './OccurenceForm'
import OccurenceItem from './OccurenceItem'
import { mergeForm } from '../reducers/form'
import { NEW } from '../utils/config'

class OccurenceManager extends Component {
  constructor () {
    super()
    this.state = {
      isAdding: false,
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
    const alreadySelectedOccurence = occurences && occurences.find(o =>
      o.beginningDatetimeMoment.isSame(datetime))
    if (alreadySelectedOccurence) {
      return
    }

    // add in the occurences form
    const eventOccurenceId = !occurences
      ? `${NEW}_0`
      : `${NEW}_${occurences.length}`
    mergeForm(
      'eventOccurences',
      eventOccurenceId, {
        beginningDatetime: datetime,
        id: eventOccurenceId,
        // TODO: SHOULD BE FIXED WITH SOON API NEW MERGE
        offer: [newOffer]
      }
    )
  }

  onAddClick = () => {
    this.setState({ isAdding: true })
  }

  render() {
    const { occurences } = this.props
    const { isAdding } = this.state
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
            {
              occurences && occurences.map(o =>
                <OccurenceItem key={o.id} {...o} />
              )
            }
            {
              isAdding && <OccurenceForm isNew />
            }
          </tbody>
        </table>
        {
          !isAdding && (
            <button className='button' onClick={this.onAddClick}>
              Ajouter un horaire
            </button>
          )
        }
      </div>
    )
  }
}

export default connect(
  (state, ownProps) => ({
    newDate: get(state, `form.datesById.${NEW}`),
    newOffer: get(state, `form.offersById${NEW}`)
  }),
  { mergeForm }
)(OccurenceManager)
