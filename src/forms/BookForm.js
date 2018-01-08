import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../reducers/request'

class BookForm extends Component {
  constructor () {
    super()
    this.state = { identifier: '' }
    this.onChange = this._onChange.bind(this)
    this.onClick = this._onClick.bind(this)
  }
  _onClick () {
    const { identifier } = this.state
    this.props.requestData('PUT', `works/isbn:${identifier}`)
  }
  _onChange ({ target: { value } }) {
    this.setState({ identifier: value })
  }
  render () {
    const { identifier } = this.state
    const { work } = this.props
    const isDisabled = identifier.trim() === ''
    return (
      <div className='book-form'>
        <div className='mb2'>
          <label className='mr2'>
            ISBN (203583418X for e.g.)
          </label>
          <input className='input mr2'
            onChange={this.onChange}
            value={identifier}
          />
          <button className={classnames('button button--alive', {
              'button--disabled': isDisabled
            })}
            disabled={isDisabled}
            onClick={this.onClick}
          >
            Recherche
          </button>
        </div>
        {
          work && (
            <div>
              <img alt='thumbnail'
                className='book__image mb1'
                src={work.thumbnailUrl}
              />
              <div>
                {work.name}
              </div>
            </div>
          )
        }
      </div>
    )
  }
}

export default connect(({ request: { works } }) => ({
  work: works && works.length === 1 && works[0]
}), { requestData })(BookForm)
