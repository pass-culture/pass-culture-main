import React, { Component } from 'react'
import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import PropTypes from 'prop-types'
import OfferTile from './OfferTile/OfferTile'
import Offers from '../domain/ValueObjects/Offers'
import { parseAlgoliaParameters } from '../domain/parseAlgoliaParameters'
import Draggable from 'react-draggable'
import { calculatePositionX, calculateStep, DEFAULT_STEP } from './domain/dragFunctions'

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

  handleStopDragging = (event, data) => {
    const { isDragging, hits, lastX, position, step } = this.state
    const firstOfferImageWidth = document.getElementsByClassName('otw-image-wrapper')[0].offsetWidth

    const maxSteps = hits.length
    const newStep = calculateStep({
      lastX: lastX,
      maxSteps: maxSteps,
      newX: data.x,
      step: step,
    })
    const newX = calculatePositionX({
      lastX: lastX,
      maxSteps: maxSteps,
      newX: data.x,
      step: step,
      width: firstOfferImageWidth
    })

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
