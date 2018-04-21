import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormTextarea from './FormTextarea'
import { mergeForm } from '../reducers/form'
import { NEW } from '../utils/config'

class MediationForm extends Component {
  componentWillMount() {
    const { mergeForm, offerId } = this.props
    mergeForm('mediations', NEW, 'name', 'Coup de Coeur')
    mergeForm('mediations', NEW, 'offerId', offerId)
  }
  render() {
    return (
      <div className="mediation-form mb2 relative p3">
        <FormTextarea
          className="textarea mediation-form__textarea mt2"
          collectionName="mediations"
          name="description"
          placeholder="donnez la description de votre coup de coeur"
        />
        {/*
        <FormInput collectionName='venuesFavorites'
          name='description'
          placeholder='donnez quelques hashtags pour cibler votre audience' />
        */}
      </div>
    )
  }
}

export default connect(null, { mergeForm })(MediationForm)
