import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import OccurenceForm from './OccurenceForm'
import Price from './Price'
import { requestData } from '../reducers/data'

class OccurenceItem extends Component {

  constructor () {
    super()
    this.state = {
      isEditing: false
    }
  }

  onEditClick = () => {

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
      beginningDatetimeMoment,
      offer
    } = this.props
    const {
      isEditing
    } = this.state

    if (isEditing) {
      return <OccurenceForm {...this.props} />
    }

    return (
      <tr className=''>
        <td>{beginningDatetimeMoment.format('DD/MM/YYYY')}</td>
        <td>{beginningDatetimeMoment.format('HH:mm')}</td>
        <td><Price value={get(offer, '0.price')} /></td>
        <td>{get(offer, '0.groupSize') || 'Illimité'}</td>
        <td>{get(offer, '0.pmrGroupSize') || 'Illimité'}</td>
        <td>
          <button
            className="delete is-small"
            onClick={this.onEditClick}
          />
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
