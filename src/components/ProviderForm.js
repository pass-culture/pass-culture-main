import React from 'react'

import FormInput from './FormInput'

const ProviderForm = ({ offererIdAtOfferProvider }) => {
  return (
    <div>
      <label className='mr1 right-align'>
        id
      </label>
      <FormInput className='input offerer-provider-form__form-input'
        collectionName='providers'
        defaultValue={offererIdAtOfferProvider}
        isRequired
        name='offererIdAtOfferProvider' />
    </div>
  )
}

export default ProviderForm
