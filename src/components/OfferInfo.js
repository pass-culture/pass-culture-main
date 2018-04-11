import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import selectOffer from '../selectors/offer'
import selectSource from '../selectors/source'
import selectThumbUrl from '../selectors/thumbUrl'
import selectVenue from '../selectors/venue'

class OfferInfo extends Component {

  formatDate(dateStr) {
    return new Date(dateStr).toLocaleString("fr-FR")
  }

  render() {
    const { offer,
      source,
      thumbUrl,
      venue,
    } = this.props;

    const infos = {
      image: thumbUrl,
      description: get(source, 'description'),
      what: get(offer, 'eventOccurence.event.description'),
      when: get(offer, 'eventOccurence.beginningDatetime') || get(offer, 'occurencesAtVenue'),
      where: {
        name: get(venue, 'name'),
        address: get(venue, 'address'),
      }
    }

    return (
      <div className='offer-info'>
        {false && <img alt='' className='offerPicture' src={infos.image} />}
        { infos.description && (
          <div className='description'>
            { infos.description.split('\n').map((p, index) =>
              <p key={index}>{p}</p>
            )}
          </div>
        )}
        { infos.what && (
          <div>
            <h3>Quoi ?</h3>
            <p>{infos.what}</p>
          </div>
        )}
        { infos.when && (
          <div>
            <h3>Quand ?</h3>
            { infos.when.constructor === Array ? (
              <ul className='dates-info'>
                { infos.when.map((occurence, index) => (
                  <li key={index}>
                    <span>{this.formatDate(occurence.beginningDatetime)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p>{this.formatDate(infos.when)}</p>
            )}
          </div>
        )}
        { infos.where.name && infos.where.address && (
          <div>
            <h3>Où ?</h3>
            <ul className='address-info'>
              <li>{infos.where.name}</li>
              {infos.where.address.split(/[,\n\r]/).map((el, index) => (<li key={index}>{el}</li>))}
            </ul>
          </div>
        )}
      </div>
    )
  }
}

export default connect(
  state => ({
    offer: selectOffer(state),
    source: selectSource(state),
    thumbUrl: selectThumbUrl(state),
    venue: selectVenue(state)
  }))(OfferInfo)
