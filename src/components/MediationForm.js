import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormTextarea from './layout/FormTextarea'
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
      <div className="mediation-form">
        <FormTextarea
          className="textarea mt2"
          collectionName="mediations"
          name="description"
          placeholder="donnez la description de votre coup de coeur"
        />
        {}
      </div>
    )
  }
}

export default connect(null, { mergeForm })(MediationForm)
