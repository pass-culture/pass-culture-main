import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import OccurenceForm from './OccurenceForm'
import Price from './Price'
import Icon from './layout/Icon'
import { requestData } from '../reducers/data'

class OccurenceItem extends Component {

  constructor () {
    super()
    this.state = {
      isEditing: false
    }
  }

  onEditClick = () => {
    this.setState({ isEditing: true })
  }

  onDeleteClick = () => {
    const {
      id,
      offer,
      requestData
    } = this.props
    requestData(
      'DELETE',
      `eventOccurences/${id}`,
      {
        key: 'eventOccurence',
        handleSuccess: () => {
          requestData(
            'DELETE',
            `offers/${offer.id}`,
            {
              key: 'offers'
            }
          )
        }
      }
    )
  }

  render () {
    const {
      occasion,
      occurences,
      occurence,
    } = this.props
    const {
      beginningDatetimeMoment,
      offer
    } = (occurence || {})
    const {
      isEditing
    } = this.state

    if (isEditing) {
      return <OccurenceForm
        occasion={occasion}
        occurence={occurence}
        occurences={occurences}
        onDeleteClick={e => this.setState({isEditing: false})}
      />
    }
    return (
      <tr className=''>
        <td>{beginningDatetimeMoment.format('DD/MM/YYYY')}</td>
        <td>{beginningDatetimeMoment.format('HH:mm')}</td>
        <td><Price value={get(offer, '0.price') || 0} /></td>
        <td>{get(offer, '0.groupSize') || 'Illimité'}</td>
        <td>{get(offer, '0.pmrGroupSize') || 'Illimité'}</td>
        <td>
          <button
            className="button is-small is-secondary"
            onClick={this.onEditClick}>
            <span className='icon'><Icon svg='ico-pen-r' /></span>
          </button>
        </td>
        <td>
          <button
            className="delete is-small"
            onClick={this.onDeleteClick}
          />
        </td>
      </tr>
    )
  }
}

export default connect(
  null,
  { requestData }
)(OccurenceItem)
