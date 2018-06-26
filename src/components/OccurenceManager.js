import React, { Component } from 'react'
import { connect } from 'react-redux'

import OccurenceForm from './OccurenceForm'
import OccurenceItem from './OccurenceItem'
import createOccurencesSelector from '../selectors/createOccurences'

class OccurenceManager extends Component {
  constructor () {
    super()
    this.state = {
      isAdding: false
    }
  }

  onAddClick = () => {
    this.setState({ isAdding: true })
  }

  render() {
    const {
      occasion,
      occurences,
    } = this.props
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
              <td></td>
            </tr>
          </thead>
          <tbody>
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
            {
              isAdding && <OccurenceForm
                occasion={occasion}
                onDeleteClick={e => this.setState({isAdding: false})}
              />
            }
          </tbody>
        </table>
        {
          !isAdding && (
            <button className='button is-secondary' onClick={this.onAddClick}>
              + Ajouter un horaire
            </button>
          )
        }
      </div>
    )
  }
}

const occurencesSelector = createOccurencesSelector()

export default connect(
 (state, ownProps) => ({
   occurences: occurencesSelector(state,
     ownProps.occasion.venueId,
     ownProps.occasion.eventId
   )
 })
)(OccurenceManager)
