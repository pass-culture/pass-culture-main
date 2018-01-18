import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import Select from './Select'
import { mergeForm } from '../reducers/form'
import { requestData } from '../reducers/data'
import { NEW } from '../utils/config'

class WorkDetector extends Component {
  constructor () {
    super()
    this.state = {
      identifier: '',
      selectedCategory: null
    }
  }
  onInputChange = ({ target: { value } }) => {
    this.setState({ identifier: value })
  }
  onOptionClick = ({ target: { value } }) => {
    this.props.mergeForm('works', NEW, 'category', value)
    this.setState({ selectedCategory: value })
  }
  onSearchClick = () => {
    const { identifier } = this.state
    this.props.requestData('GET', `works/book:${identifier}`, { key: 'works'})
  }
  render () {
    const { identifier, selectedCategory } = this.state
    const { options, work } = this.props
    const isDisabled = identifier.trim() === ''
    return (
      <div className='work-detector p2'>
        {
          !work && <Select className='select mb2'
            defaultLabel='-- choisir une catégorie --'
            onOptionClick={this.onOptionClick}
            options={options}
            value={selectedCategory}
          />
        }
        {
          selectedCategory && (
            <div className='mb2 sm-col-6 mx-auto'>
              <label className='block left-align mb1'>
                {
                  selectedCategory === 'book'
                    ? 'ISBN (0140188711 for e.g.)'
                    : 'Identifiant'
                }
              </label>
              <div className='flex items-center'>
                <input className='input mr2 left-align'
                  onChange={this.onInputChange}
                  value={identifier}
                />
                <button className={classnames('button button--alive', {
                    'button--disabled': isDisabled
                  })}
                  disabled={isDisabled}
                  onClick={this.onSearchClick}
                >
                  Recherche
                </button>
              </div>
            </div>
          )
        }
      </div>
    )
  }
}

WorkDetector.defaultProps = {
  options: [
    { value: 'book', label: 'Livre' },
    { value: 'theater', label: 'Theâtre' }
  ]
}

export default connect(
  state => ({ work: state.data.works && state.data.works[0] }),
  { mergeForm, requestData }
)(WorkDetector)
