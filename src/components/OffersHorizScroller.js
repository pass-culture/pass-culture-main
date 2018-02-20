import React, { Component } from 'react'
import { connect } from 'react-redux'

import OffersCaroussel from './OffersCaroussel'
import { requestData } from '../reducers/data'
import { syncUserMediations } from '../utils/sync'

class OffersHorizScroller extends Component {
  handleRequestData (props) {
    const { requestData, userId } = props
    /*
    userId && requestData('GET',
      'offers?hasPrice=true&&removeDisliked=true',
      { isGeolocated: true }
    )
    */
    userId && requestData('GET',
      'userMediations',
      { isGeolocated: true, sync: true }
    )
  }
  componentWillMount () {
    this.handleRequestData(this.props)
    // syncUserMediations()
  }
  componentWillReceiveProps (nextProps) {
    if (nextProps.userId && (!this.props.userId || nextProps.userId !== this.props.userId)) {
      this.handleRequestData(nextProps)
    }
  }
  render = () => {
    const { carousselsCount, offers } = this.props
    return (
      <div className={`offer-horiz-scroller offer-horiz-scroller--${carousselsCount}`}>
        {
          offers && offers.length > 0
            ? [...Array(carousselsCount).keys()]
                .map(index => (
                    <OffersCaroussel carousselsCount={carousselsCount}
                      key={index}
                      modulo={index}
                      offers={offers} />
                ))
            : <div className='no-offers'>Aucune offre à afficher</div>
        }
      </div>
    )
  }
}

OffersHorizScroller.defaultProps = {
  carousselsCount: 1
}

export default connect(
   state => ({ offers: state.data.offers, userId: state.user && state.user.id }),
   { requestData }
 )(OffersHorizScroller)
