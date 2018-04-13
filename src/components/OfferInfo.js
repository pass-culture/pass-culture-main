import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import moment from 'moment'

import Icon from './Icon'
import { navigationLink } from '../utils/geolocation'
import selectDistance from '../selectors/distance'
import selectOffer from '../selectors/offer'
import selectSource from '../selectors/source'
import selectThumbUrl from '../selectors/thumbUrl'
import selectVenue from '../selectors/venue'
import selectUserMediation from '../selectors/userMediation'


class OfferInfo extends Component {

  render() {
    const {
      distance,
      offer,
      source,
      thumbUrl,
      venue,
      userMediation,
    } = this.props;

    const infos = {
      image: thumbUrl,
      description: get(source, 'description'),
      what: get(offer, 'eventOccurence.event.description'),
      when: get(userMediation, 'mediatedOccurences', []).map(o => o.beginningDatetime),
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
            <ul className='dates-info'>
              { infos.when.map((occurence, index) => (
                <li key={index}>
                  <span>{moment(occurence).format('DD/MM/YYYY à H:mm')}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        { infos.where.name && infos.where.address && (
          <div>
            <h3>Où ?</h3>
            <a className='distance' href={navigationLink(venue.latitude, venue.longitude)}>
              { distance }
              <Icon svg='ico-geoloc-solid2' />
            </a>
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
    distance: selectDistance(state),
    offer: selectOffer(state),
    source: selectSource(state),
    thumbUrl: selectThumbUrl(state),
    userMediation: selectUserMediation(state),
    venue: selectVenue(state)
  }))(OfferInfo)
