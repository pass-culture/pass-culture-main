import get from 'lodash.get'
import moment from 'moment'
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
      isEditing: false
    }
  }

  onAddClick = () => {
    const {
      mergeForm,
      occurences,
    } = this.props

    const lastOccurence = occurences.length > 0 && occurences[occurences.length-1]
    if (lastOccurence) {
      const {
        beginningDatetime,
        endDatetime,
        offer
      } = lastOccurence
      const {
        available,
        groupSize,
        pmrGroupSize,
        price
      } = get(offer, '0', {})
      const date = moment(beginningDatetime).add(1, 'days')
      mergeForm('eventOccurences', NEW,
        {
          available,
          date,
          time: date.format('HH:mm'),
          endTime: moment(endDatetime).add(1, 'days').format('HH:mm'),
          groupSize,
          pmrGroupSize,
          price: typeof price === 'undefined'
            ? 0
            : price
        })
    }

    this.setState({ isAdding: true })
  }

  onEditChange = (isEditing) => {
    this.setState({ isEditing })
  }

  render() {
    const {
      occasion,
      occurences,
    } = this.props
    const { isAdding, isEditing } = this.state

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
                <td>Dont (PMR)</td>
                <td>Supprimer</td>
                <td>Modifier</td>
              </tr>
            </thead>
            <tbody>
              {
                isAdding ? (<OccurenceForm
                  occasion={occasion}
                  onDeleteClick={e => this.setState({isAdding: false})}
                  onEditChange={this.onEditChange}
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
                    isAdding={isAdding}
                    isEditing={isEditing}
                    occasion={occasion}
                    occurence={o}
                    occurences={occurences}
                    onEditChange={this.onEditChange}
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
                </tr>
              </thead>
            )}
          </table>
        </div>
      </div>
    )
  }
}

export default connect(null, { mergeForm })(OccurenceManager)
