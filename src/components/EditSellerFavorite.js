import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormInput from './FormInput'
import FormTextarea from './FormTextarea'
import Icon from './Icon'
import { assignForm } from '../reducers/form'

class EditSellerFavorite extends Component {
  componentWillMount () {
    const { assignForm, offerId } = this.props
    assignForm({ offerId })
  }
  render () {
    return (
      <div className='edit-seller-favorite mb2 p3 relative'>
        <div className='seller-favorite__icon absolute'>
          <Icon name='favorite-outline' />
        </div>
        <FormTextarea className='textarea edit-seller-favorite__textarea mt2'
          name='sellersFavoriteDescription'
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

export default connect(null, { assignForm })(EditSellerFavorite)
