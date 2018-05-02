import React from 'react'

import FormInput from './layout/FormInput'

const ProviderForm = ({ offererIdAtOfferProvider }) => {
  return (
    <div>
      <label className="mr1 right-align">id</label>
      <FormInput
        className="input"
        collectionName="providers"
        defaultValue={offererIdAtOfferProvider}
        isRequired
        name="offererIdAtOfferProvider"
      />
    </div>
  )
}

export default ProviderForm
