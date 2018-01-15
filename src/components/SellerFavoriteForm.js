import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormInput from './FormInput'
import FormTextarea from './FormTextarea'
import Icon from './Icon'
import { assignForm } from '../reducers/form'

class SellerFavoriteForm extends Component {
  componentWillMount () {
    const { assignForm, offerId } = this.props
    assignForm({ offerId })
  }
  render () {
    return (
      <div className='seller-favorite-form mb2 p3 relative'>
        <div className='seller-favorite__icon absolute'>
          <Icon name='favorite-outline' />
        </div>
        <FormTextarea className='textarea seller-favorite-form__textarea mt2'
          name='description'
          placeholder='donnez la description de votre coup de coeur' />
        {
          /*<FormInput name='description'
          placeholder='donnez quelques hashtags pour cibler votre audience' />
          */
        }
      </div>
    )
  }
}

export default connect(null, { assignForm })(SellerFavoriteForm)
