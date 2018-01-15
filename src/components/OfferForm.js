import React from 'react'

import FormInput from './FormInput'
import FormTextarea from './FormTextarea'
import SubmitButton from './SubmitButton'

const OfferForm = ({ description,
  name,
  thumbnailUrl,
  work
}) => {
  return (
    <div className='offer-form'>
      <FormInput className='input mt1 mb3'
        defaultValue={name}
        name='name'
        placeholder="titre de l'offre"
      />
      <div className='offer-form__content flex flex-wrap items-center justify-around mb2 p1'>
        <img alt='thumbnail'
          className='offer-form__content__img mb1'
          src={thumbnailUrl || work.thumbnailUrl} />
        <FormTextarea className='textarea offer-form__content__textarea'
          defaultValue={description}
          name='description'
          placeholder="Vous pouvez écrire un description ici" >
          {description}
        </FormTextarea>
      </div>
      <SubmitButton className='button button--alive mb2'
        getOptimistState={(state, action) => {
          return { newOffer: action.config.body }
        }}
        path='offers' />
    </div>
  )
}

export default OfferForm
