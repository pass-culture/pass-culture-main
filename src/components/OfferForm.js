import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormInput from './FormInput'
import FormTextarea from './FormTextarea'
import { mergeForm } from '../reducers/form'
import { API_URL } from '../utils/config'

class OfferForm extends Component {
  componentWillMount () {
    this.handleMergeForm(this.props)
  }
  componentWillReceiveProps (nextProps) {
    if (
      // be sure to put the id inside the form (even after a reset form)
      !nextProps.formOffer ||
      nextProps.id !== this.props.id
    ) {
      this.handleMergeForm(nextProps)
    }
  }
  handleMergeForm = props => {
    const { id, mergeForm } = props
    id && mergeForm('offers', id, 'id', id)
  }
  render () {
    const { description,
      id,
      name,
      thumbnailUrl,
      work
    } = this.props
    return (
      <div className='offer-form p2'>
        <div className='mb2'>
          <label className='block mb1'>
            titre
          </label>
          <FormInput className='input col-12'
            collectionName='offers'
            defaultValue={name || work.name}
            id={id}
            name='name'
            placeholder="titre de l'offre"
          />
        </div>
        <div>
          <label className='block mb1'>
            description
          </label>
          <FormTextarea className='textarea offer-form__textarea'
            collectionName='offers'
            defaultValue={description || work.description}
            id={id}
            maxLength={1000}
            name='description'
            placeholder="Vous pouvez écrire une description ici" />
        </div>
      </div>
    )
  }
}

export default connect(
  (state, ownProps) => ({ formOffer: state.form.offersById && state.form.offersById[ownProps.id] }),
  { mergeForm }
)(OfferForm)
