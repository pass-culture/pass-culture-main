import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import OccurenceForm from './OccurenceForm'
import OccurenceItem from './OccurenceItem'
import { mergeForm } from '../reducers/form'
import createOccurencesSelector from '../selectors/createOccurences'
import { NEW } from '../utils/config'

class OccurenceManager extends Component {
  constructor () {
    super()
    this.state = {
      isAdding: false
    }
  }

  onAddClick = () => {
    const {
      mergeForm,
      occurences,
    } = this.props

    const lastOccurence = occurences.length > 0 && occurences[occurences.length-1]
    if (lastOccurence) {
      const date = moment(lastOccurence.beginningDatetime).add(1, 'days')
      console.log(lastOccurence)
      mergeForm('eventOccurences',
                NEW,
                {
                  date: date,
                  time: date.format('HH:mm'),
                  endTime: moment(lastOccurence.endDatetime).add(1, 'days').format('HH:mm'),
                  groupSize: get(lastOccurence, 'offer.0.groupSize'),
                  pmrGroupSize: get(lastOccurence, 'offer.0.pmrGroupSize'),
                  price: get(lastOccurence, 'offer.0.price'),
                }
               )
    }

    this.setState({ isAdding: true })
  }

  render() {
    const {
      occasion,
      occurences,
    } = this.props
    const { isAdding } = this.state

    return (
      <div className='occurence-manager'>
        <div className='occurence-table-wrapper'>
          <table className='table is-hoverable occurence-table'>
            <thead>
              <tr>
                <td>Date</td>
                <td>Heure de début</td>
                <td>Heure de fin</td>
                <td>Prix</td>
                <td>Places (total)</td>
                <td>Dont PMR</td>
                <td>Supprimer</td>
                <td>Modifier</td>
                <td>Dupliquer J+1</td>
              </tr>
            </thead>
            <tbody>
              {
                isAdding ? (<OccurenceForm
                  occasion={occasion}
                  onDeleteClick={e => this.setState({isAdding: false})}
                />) : (
                  <tr><td colspan='10'>
                    <button className='button is-secondary' onClick={this.onAddClick}>
                      + Ajouter un horaire
                    </button>
                  </td></tr>
                )
              }
              {
                occurences && occurences.map(o =>
                  <OccurenceItem
                    key={o.id}
                    occasion={occasion}
                    occurence={o}
                    occurences={occurences}
                  />
                )
              }
            </tbody>
            {occurences.length > 12 && (
              <thead>
                <tr>
                  <td>Date</td>
                  <td>Heure de début</td>
                  <td>Heure de fin</td>
                  <td>Prix</td>
                  <td>Places (total)</td>
                  <td>Dont PMR</td>
                  <td>Supprimer</td>
                  <td>Modifier</td>
                  <td>Dupliquer J+1</td>
                </tr>
              </thead>
            )}
          </table>
        </div>
      </div>
    )
  }
}

const occurencesSelector = createOccurencesSelector()

export default connect(
 (state, ownProps) => ({
   occurences: occurencesSelector(state,
     get(ownProps, 'occasion.venueId'),
     get(ownProps, 'occasion.eventId')
   )
 }),
  { mergeForm }
)(OccurenceManager)
