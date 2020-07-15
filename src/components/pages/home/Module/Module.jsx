import React, { Component } from 'react'
import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import PropTypes from 'prop-types'
import OfferTile from './OfferTile/OfferTile'
import Offers from '../domain/ValueObjects/Offers'
import { parseAlgoliaParameters } from '../domain/parseAlgoliaParameters'
import Draggable from 'react-draggable'

const DEFAULT_STEP = 0

class Module extends Component {
  constructor(props) {
    super(props)
    this.state = {
      hits: [],
      isDragging: false,
      lastX: 0,
      position: { x: 0, y: 0 },
      step: DEFAULT_STEP
    }
  }

  componentDidMount() {
    const { module: { algolia } } = this.props
    const parsedParameters = parseAlgoliaParameters(algolia)

    fetchAlgolia(parsedParameters).then(data => {
      const { hits } = data
      this.setState({
        hits: hits
      })
    })
  }

  calculatePositionX = (lastX, newX, position, step, maxSteps) => {
    const width = document.getElementsByClassName('otw-image-wrapper')[0].offsetWidth
    const movingRight = lastX > newX
    const movingRatio = width * 1.035

    if (movingRight) {
      if (step < maxSteps) {
        return position.x - movingRatio
      }
      return position.x
    } else {
      if (step > 0) {
        return position.x + movingRatio
      }
      return position.x
    }
  }

  calculateStep = (lastX, newX, step, maxSteps) => {
    const movingRight = lastX > newX

    if (movingRight) {
      if (step < maxSteps) {
        return step + 1
      }
      return maxSteps
    } else {
      if (step > 0) {
        return step - 1
      }
      return DEFAULT_STEP
    }
  }

  handleStopDragging = (event, data) => {
    const { isDragging, hits, lastX, position, step } = this.state
    const maxSteps = hits.length - 1
    const newStep = this.calculateStep(lastX, data.x, step, maxSteps)
    const newX = this.calculatePositionX(lastX, data.x, position, step, maxSteps)

    if (isDragging) {
      this.setState({
        isDragging: false,
        lastX: newX,
        position: {
          x: newX,
          y: position.y
        },
        step: newStep
      })
    }
  }

  handleDragging = () => {
    this.setState({
      isDragging: true
    })
  }

  render() {
    const { module: { display } } = this.props
    const { hits, position } = this.state
    const atLeastOneHit = hits.length > 0

    return atLeastOneHit ?
      <div className="module-wrapper">
        <h1>
          {display.title}
        </h1>
        <Draggable
          axis="x"
          bounds={{ right: 0 }}
          onDrag={this.handleDragging}
          onStop={this.handleStopDragging}
          position={position}
        >
          <ul
            className={display.layout}
          >
            {hits.map(hit => (
              <OfferTile
                hit={hit}
                key={hit.offer.id}
              />)
            )}
          </ul>
        </Draggable>
      </div>
      : <div />
  }
}

Module.propTypes = {
  module: PropTypes.instanceOf(Offers).isRequired
}

export default Module
