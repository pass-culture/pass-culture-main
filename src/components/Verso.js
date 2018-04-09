import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import OfferInfo from '../components/OfferInfo'
import VersoWrapper from '../components/VersoWrapper'
import MenuButton from '../components/layout/MenuButton'
import selectIsTuto from '../selectors/isTuto'
import selectMediation from '../selectors/mediation'
import { THUMBS_URL } from '../utils/config'

class Verso extends Component {

  render() {
    const { isFlipped,
            isTuto,
            mediation,
          } = this.props
    return (
      <div className={classnames('verso', {
        'flipped': isFlipped,
      })} >
        <VersoWrapper hasControlBar={!isTuto} className='with-padding-top'>
          {
            isTuto
            ? mediation && <img alt='verso'
                className='verso-tuto-mediation'
                src={`${THUMBS_URL}/mediations/${mediation.id}_1`} />
            : <OfferInfo />
          }
        </VersoWrapper>
        <MenuButton borderTop colored />
      </div>
    )
  }
}

export default connect(
  state => ({
    isFlipped: state.navigation.isFlipped,
    isTuto: selectIsTuto(state),
    mediation: selectMediation(state),
  }))(Verso)
