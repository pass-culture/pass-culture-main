import classnames from 'classnames'
import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import withSizes from 'react-sizes'
import { compose } from 'redux'

import Recto from './Recto'
import Verso from './Verso'
import { requestData } from '../reducers/data'
import selectCurrentHeaderColor from '../selectors/currentHeaderColor'
import { IS_DEXIE } from '../utils/config'


class Card extends Component {

  componentDidUpdate (prevProps) {
    const { isFlipped,
      position,
      recommendation,
      requestData
    } = this.props
    if (recommendation && position === 'current') {
      if (!prevProps.isFlipped && isFlipped && !recommendation.isClicked) {
        requestData('PATCH', `recommendations/${recommendation.id}`,
          {
            body: {
              isClicked: true
            },
            key: 'recommendations',
            local: IS_DEXIE
          }
        )
      }
    }
  }

  render() {
    const {
      currentHeaderColor,
      recommendation,
      position,
      width
    } = this.props
    return (
      <div
        className={classnames('card', {
          current: position === 'current',
        })}
        style={{
          transform: `translate(${get(recommendation, 'index') * width}px, 0)`,
          backgroundColor: currentHeaderColor,
        }}
      >
        <Recto {...recommendation} />
        {position === 'current' && <Verso />}
      </div>
    )
  }
}

Card.defaultProps = {
  readTimeout: 3000
}

export default compose(
  withSizes(({ width, height }) => ({
    width: Math.min(width, 500), // body{max-width: 500px;}
    height,
  })),
  connect(
    state => ({
      currentHeaderColor: selectCurrentHeaderColor(state),
      isFlipped: state.verso.isFlipped,
    }),
    { requestData }
  )
)(Card)
