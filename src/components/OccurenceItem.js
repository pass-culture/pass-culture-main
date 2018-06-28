import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import OccurenceForm from './OccurenceForm'
import Price from './Price'
import Icon from './layout/Icon'
import { requestData } from '../reducers/data'
import createEventSelector from '../selectors/createEvent'
import createTimezoneSelector from '../selectors/createTimezone'
import createVenueSelector from '../selectors/createVenue'

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

  onDuplicateClick = () => {

  }

  onDeleteClick = () => {
    const {
      occurence,
      requestData
    } = this.props
    const {
      id,
      offer
    } = occurence
    requestData(
      'DELETE',
      `eventOccurences/${id}`,
      {
        key: 'eventOccurences',
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
      tz
    } = this.props
    const {
      beginningDatetimeMoment,
      endDatetimeMoment,
      offer
    } = (occurence || {})
    const beginningDatetimeMomentTz = beginningDatetimeMoment.clone().tz(tz)
    const endDatetimeMomentTz = endDatetimeMoment.clone().tz(tz)
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
        <td>{beginningDatetimeMomentTz.format('DD/MM/YYYY')}</td>
        <td>{beginningDatetimeMomentTz.format('HH:mm')}</td>
        <td>{endDatetimeMomentTz.format('HH:mm')}</td>
        <td><Price value={get(offer, '0.price') || 0} /></td>
        <td>{get(offer, '0.available') || 'Illimité'}</td>
        <td>{get(offer, '0.pmrGroupSize') || 'Illimité'}</td>
        <td>
          <button
            className="button is-small is-secondary"
            onClick={this.onDeleteClick}
          >
            <span className='icon'><Icon svg='ico-close-r' /></span>
          </button>
        </td>
        <td>
          <button
            className="button is-small is-secondary"
            onClick={this.onEditClick}>
            <span className='icon'><Icon svg='ico-pen-r' /></span>
          </button>
        </td>
        <td>
          <button
            className="button is-small is-secondary"
            onClick={this.onDuplicateClick}>
            <span className='icon'><Icon svg='ico-offres-r' /></span>
          </button>
        </td>

      </tr>
    )
  }
}

const venueSelector = createVenueSelector()
const timezoneSelector = createTimezoneSelector(venueSelector)


export default connect(
  (state, ownProps) => ({
    tz: timezoneSelector(state, get(ownProps, 'occasion.venueId'))
  }),
  { requestData }
)(OccurenceItem)
