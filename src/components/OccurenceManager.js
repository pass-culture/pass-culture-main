import React, { Component } from 'react'
import { connect } from 'react-redux'

import OccurenceForm from './OccurenceForm'
import OccurenceItem from './OccurenceItem'
import selectCurrentOccurences from '../selectors/currentOccurences'

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
      occasion
    } = this.props
    const {
      occurences,
    } = occasion
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
                <OccurenceItem key={o.id} occurence={o} occasion={occasion} />
              )
            }
            {
              isAdding && <OccurenceForm
                onDeleteClick={e => this.setState({isAdding: false})}
                occasion={occasion}
                isNew
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

export default OccurenceManager

// export default connect(
//   (state, ownProps) => ({
//     currentOccurences: selectCurrentOccurences(state, ownProps)
//   })
// )(OccurenceManager)
