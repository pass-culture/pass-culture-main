import React, { Component } from 'react'
import { connect } from 'react-redux'

import OffersCaroussel from './OffersCaroussel'
import { requestData } from '../reducers/data'

class OffersHorizScroller extends Component {
  componentWillMount = () => {
    const { requestData } = this.props;
    requestData('GET', `offers?hasPrice=true`)
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
   state => ({ offers: state.data.offers }),
   { requestData }
 )(OffersHorizScroller)
