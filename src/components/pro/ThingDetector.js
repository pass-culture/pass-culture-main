import React, { Component } from 'react'
import { connect } from 'react-redux'

import Select from '../layout/Select'
import { mergeForm } from '../../reducers/form'
import { requestData } from '../../reducers/data'
import { NEW } from '../../utils/config'

class ThingDetector extends Component {
  constructor() {
    super()
    this.state = {
      identifier: '',
      selectedCategory: null,
    }
  }
  onInputChange = ({ target: { value } }) => {
    this.setState({ identifier: value })
  }
  onOptionClick = ({ target: { value } }) => {
    this.props.mergeForm('things', NEW, 'category', value)
    this.setState({ selectedCategory: value })
  }
  onSearchClick = () => {
    const { identifier } = this.state
    this.props.requestData('GET', `things/book:${identifier}`, {
      key: 'things',
    })
  }
  render() {
    const { identifier, selectedCategory } = this.state
    const { options, thing } = this.props
    const isDisabled = identifier.trim() === ''
    return (
      <div className="thing-detector p2">
        {!thing && (
          <Select
            className="select mb2"
            defaultLabel="-- choisir une catégorie --"
            onOptionClick={this.onOptionClick}
            options={options}
            value={selectedCategory}
          />
        )}
        {selectedCategory && (
          <div className="mb2 mx-auto">
            <label className="block left-align mb1">
              {selectedCategory === 'book'
                ? 'ISBN (0140188711 for e.g.)'
                : 'Identifiant'}
            </label>
            <div className="flex items-center">
              <input
                className="input mr2 left-align"
                onChange={this.onInputChange}
                value={identifier}
              />
              <button
                className="button is-default"
                disabled={isDisabled}
                onClick={this.onSearchClick}
              >
                Recherche
              </button>
            </div>
          </div>
        )}
      </div>
    )
  }
}

ThingDetector.defaultProps = {
  options: [
    { value: 'book', label: 'Livre' },
    { value: 'theater', label: 'Theâtre' },
  ],
}

export default connect(
  state => ({ thing: state.data.things && state.data.things[0] }),
  { mergeForm, requestData }
)(ThingDetector)
