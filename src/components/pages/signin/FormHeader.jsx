import React from 'react'

const FormHeader = () => (
  <div className="mb36">
    <h1 className="text-left fs32">
      <span className="is-bold is-italic is-block">{'Bonjour !'}</span>
    </h1>
    <p className="text-left is-italic is-medium fs22">
      <span className="is-block">{'Identifiez-vous'}</span>
      <span className="is-block">{'pour accéder aux offres.'}</span>
    </p>
    <p className="fs13 mt18">
      <span>{'* Champs obligatoires'}</span>
    </p>
  </div>
)
export default FormHeader
