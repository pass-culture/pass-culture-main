import React, { Component } from 'react'
import { connect } from 'react-redux'

// import FormInput from './FormInput'
import FormTextarea from './FormTextarea'
import { mergeForm } from '../reducers/form'
import { NEW } from '../utils/config'

class FavoriteForm extends Component {
  componentWillMount () {
    const { mergeForm, offerId } = this.props
    mergeForm('venuesFavorites', NEW, 'offerId', offerId)
  }
  render () {
    return (
      <div className='favorite-form mb2 relative p3'>
        <FormTextarea className='textarea favorite-form__textarea mt2'
          collectionName='venuesFavorites'
          name='comment'
          placeholder='donnez la description de votre coup de coeur' />
        {/*
        <FormInput collectionName='venuesFavorites'
          name='description'
          placeholder='donnez quelques hashtags pour cibler votre audience' />
        */}
      </div>
    )
  }
}

export default connect(null, { mergeForm })(FavoriteForm)
