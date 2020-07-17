import PropTypes from 'prop-types'
import React, { Component } from 'react'
import Draggable from 'react-draggable'

import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import { parseAlgoliaParameters } from '../domain/parseAlgoliaParameters'
import Offers from '../domain/ValueObjects/Offers'
import { DEFAULT_POSITION, DEFAULT_STEP } from '../_constants'
import { calculatePositionOnXAxis, calculateStep } from './domain/dragFunctions'
import OfferTile from './OfferTile/OfferTile'

class Module extends Component {
  constructor(props) {
    super(props)
    this.state = {
      hits: [],
      lastPositionOnXAxis: 0,
      position: DEFAULT_POSITION,
      step: DEFAULT_STEP,
    }
  }

  componentDidMount() {
    const {
      module: { algolia },
    } = this.props
    const parsedParameters = parseAlgoliaParameters(algolia)

    fetchAlgolia(parsedParameters).then(data => {
      const { hits } = data
      this.setState({
        hits: hits,
      })
    })
  }

  moveToPreviousOrNextTile = (event, data) => {
    const { hits, lastPositionOnXAxis, position, step } = this.state
    const firstOfferImageWidth = document.getElementsByClassName('otw-image-wrapper')[0].offsetWidth

    const maxSteps = hits.length
    const newStep = calculateStep({
      lastPositionOnXAxis: lastPositionOnXAxis,
      maxSteps: maxSteps,
      newPositionOnXAxis: data.x,
      step: step,
    })
    const newPositionOnXAxis = calculatePositionOnXAxis({
      lastPositionOnXAxis: lastPositionOnXAxis,
      maxSteps: maxSteps,
      newPositionOnXAxis: data.x,
      step: step,
      width: firstOfferImageWidth,
    })

    this.setState({
      lastPositionOnXAxis: newPositionOnXAxis,
      position: {
        x: newPositionOnXAxis,
        y: position.y,
      },
      step: newStep,
    })

    this.getAllLinks().forEach(link => {
      link.classList.remove('disabled-click-event')
    })
  }

  removeClickableLinks = () => {
    this.getAllLinks().forEach(link => {
      link.classList.add('disabled-click-event')
    })
  }

  getAllLinks = () => window.document.querySelectorAll('.hw-modules a')

  preventDefaultLink = event => {
    event.preventDefault()
  }

  render() {
    const {
      module: { display },
      row,
    } = this.props
    const { hits, position } = this.state
    const atLeastOneHit = hits.length > 0

    return (
      atLeastOneHit && (
        <div className="module-wrapper">
          <h1>
            {display.title}
          </h1>
          <Draggable
            axis="x"
            bounds={{ right: 0 }}
            onDrag={this.removeClickableLinks}
            onMouseDown={this.preventDefaultLink}
            onStop={this.moveToPreviousOrNextTile}
            position={position}
          >
            <ul className={display.layout}>
              {hits.map(hit => (
                <OfferTile
                  hit={hit}
                  key={`${row}${hit.offer.id}`}
                />
              ))}
            </ul>
          </Draggable>
        </div>
      )
    )
  }
}

Module.propTypes = {
  module: PropTypes.instanceOf(Offers).isRequired,
  row: PropTypes.number.isRequired,
}

export default Module
