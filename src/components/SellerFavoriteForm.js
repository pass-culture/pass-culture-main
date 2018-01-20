import React, { Component } from 'react'
import { connect } from 'react-redux'

// import FormInput from './FormInput'
import FormTextarea from './FormTextarea'
import { mergeForm } from '../reducers/form'
import { NEW } from '../utils/config'

class SellerFavoriteForm extends Component {
  componentWillMount () {
    const { mergeForm, offerId } = this.props
    mergeForm('sellersFavorites', NEW, 'offerId', offerId)
  }
  render () {
    return (
      <div className='seller-favorite-form mb2 relative p3'>
        <FormTextarea className='textarea seller-favorite-form__textarea mt2'
          collectionName='sellersFavorites'
          name='comment'
          placeholder='donnez la description de votre coup de coeur' />
        {/*
        <FormInput collectionName='sellersFavorites'
          name='description'
          placeholder='donnez quelques hashtags pour cibler votre audience' />
        */}
      </div>
    )
  }
}

export default connect(null, { mergeForm })(SellerFavoriteForm)
