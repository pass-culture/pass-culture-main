import React, { useState } from 'react'

import HeaderContainer from '../../../layout/Header/HeaderContainer'
import EditPasswordField from "../EditPassword/EditPasswordField/EditPasswordField";
import PersonalInformationsField from "../PersonalInformations/PersonalInformationsField/PersonalInformationsField";
import { checkIfEmailIsValid } from "../../create-account/domain/checkIfEmailIsValid";
import { API_URL } from "../../../../utils/config"

const EditEmail = () => {

  const [ email, setEmail ] = useState('')
  const [ password, setPassword ] = useState('')
  const [ emailErrors, setEmailErrors ] = useState()
  const [ passwordErrors, setPasswordErrors ] = useState()

  const onEmailChange = (event) => {
    const email = event.target.value
    setEmail(email)

    if (!checkIfEmailIsValid(email)) {
      setEmailErrors([ "Format de l'e-mail incorrect" ])
    } else {
      setEmailErrors(null)
    }
  }

  const onFormSubmit = (event) => {
    event.preventDefault()
    console.log(email)
    console.log(password)
    const payload = {
      new_email: email,
      password: password
    }

    return fetch(`${API_URL}/beneficiaries/change_email_request`, {
      body: JSON.stringify(payload),
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      method: 'PUT',
    })
      .then(response => response.json())
      .then(result => {
        console.log(result)

        if(result.password) {
          setPasswordErrors(result.password)
        }

      })
      .catch(e => {
        console.warn(e)
      })
  }

  return (
    <main className="pf-container pf-email">
      <HeaderContainer
        backTo="/profil/informations"
        title="Adresse e-mail"
      />
      <p className='pf-email-explanation'>
        Pour plus de sécurité, saisis ton mot de passe !<br/>
        Tu recevras un e-mail avec un lien à activer pour confirmer la modification de ton adresse.
      </p>

      <form
        className="pf-form"
        onSubmit={onFormSubmit}
      >
        <div>
          <PersonalInformationsField
            autocomplete="off"
            errors={emailErrors}
            label="E-mail"
            name="new-email"
            onChange={onEmailChange}
            required
            value={email}
          />

          <EditPasswordField
            autocomplete="off"
            errors={passwordErrors}
            label="Mot de passe"
            name="password"
            onChange={(event) => setPassword(event.target.value)}
            required
            value={password}
          />
        </div>

        <div className="pf-form-submit">
          <input
            className="pf-button-submit"
            type="submit"
            value="Enregistrer"
            onChange={onFormSubmit}
          />
        </div>
      </form>
    </main>
  )
}


EditEmail.propTypes = {}

export default EditEmail
