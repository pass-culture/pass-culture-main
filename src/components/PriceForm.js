import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormInput from './FormInput'
import { mergeForm } from '../reducers/form'
import { NEW } from '../utils/config'

class PriceForm extends Component {
  componentWillMount () {
    const { mergeForm, offerId } = this.props
    mergeForm('prices', NEW, 'offerId', offerId)
  }
  render () {
    const { endDate, startDate, groupSize, value } = this.props
    return (
      <div className='price-form mb2 mx-auto p3 clearfix'>
        <div className='md-col md-col-6 relative mb2'>
          <label className='mr1 right-align'>
            à partir de
          </label>
          <FormInput className='input price-form__form-input price-form__form-input--group-size mb1'
            collectionName='prices'
            defaultValue={groupSize}
            isRequired
            name='groupSize'
            type='number'
          />
          <span className='absolute price-form__suffix'>
            pers.
          </span>
          <br />
          <label className='mr1 right-align'>
            prix
          </label>
          <FormInput className='input price-form__form-input'
            collectionName='prices'
            defaultValue={value}
            isRequired
            name='value'
          />
        </div>
        <div className='md-col md-col-6'>
          <label className='mr1 right-align'>
            début
          </label>
          <FormInput className='input price-form__form-input mb1'
            collectionName='prices'
            defaultValue={startDate}
            name='startDate'
            type='date'
          />
          <br />
          <label className='mr1 right-align'>
            fin
          </label>
          <FormInput className='input price-form__form-input'
            collectionName='prices'
            defaultValue={endDate}
            name='endDate'
            type='date'
          />
          <br />
        </div>
      </div>
    )
  }
}

export default connect(null, { mergeForm })(PriceForm)
