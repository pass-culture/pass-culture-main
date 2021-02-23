import React, { createRef, useCallback, useState } from 'react'

import HeaderContainer from '../../../layout/Header/HeaderContainer'
import EditPasswordField from '../EditPassword/EditPasswordField/EditPasswordField'
import PersonalInformationsField from '../PersonalInformations/PersonalInformationsField/PersonalInformationsField'
import { checkIfEmailIsValid } from '../../create-account/domain/checkIfEmailIsValid'
import { updateEmail } from '../repository/updateEmail'
import { toast } from 'react-toastify'
import PropTypes from 'prop-types'

const EditEmail = ({ redirectToPersonnalInformationPage }) => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [emailErrors, setEmailErrors] = useState(null)
  const [passwordErrors, setPasswordErrors] = useState()

  const _handleSubmit = useCallback(
    event => {
      event.preventDefault()
      const payload = {
        new_email: email,
        password: password,
      }

      return updateEmail(payload)
        .then(async result => {
          if (result.status === 204) {
            setPasswordErrors(null)
            toast.success('L’e-mail a bien été envoyé.')
            return redirectToPersonnalInformationPage()
          }

          const answer = await result.json()

          if (answer.password) setPasswordErrors(answer.password)
        })
        .catch(() => {
          toast.error('La modification de l’adresse e-mail a échoué.')
        })
    },
    [email, password, redirectToPersonnalInformationPage]
  )

  const _handleEmailChange = useCallback(event => {
    const email = event.target.value
    setEmail(email)

    if (!checkIfEmailIsValid(email)) {
      setEmailErrors(["Format de l'e-mail incorrect"])
    } else {
      setEmailErrors(null)
    }
  }, [])

  const _handlePasswordChange = useCallback(event => setPassword(event.target.value), [])

  return (
    <main className="pf-container pf-email">
      <HeaderContainer
        backTo="/profil/informations"
        title="Adresse e-mail"
      />
      <p className="pf-email-explanation">
        {'Pour plus de sécurité, saisis ton mot de passe !'}
        <br />
        {
          'Tu recevras un e-mail avec un lien à activer pour confirmer la modification de ton adresse.'
        }
      </p>

      <form
        className="pf-form"
        onSubmit={_handleSubmit}
      >
        <div>
          <PersonalInformationsField
            autocomplete="off"
            errors={emailErrors}
            label="E-mail"
            name="new-email"
            onChange={_handleEmailChange}
            required
            value={email}
          />

          <EditPasswordField
            autocomplete="off"
            errors={passwordErrors}
            inputRef={createRef()}
            label="Mot de passe"
            name="password"
            onChange={_handlePasswordChange}
            required
            value={password}
          />
        </div>

        <div className="pf-form-submit">
          <input
            className="pf-button-submit"
            disabled={!password || !email || emailErrors !== null}
            onChange={_handleSubmit}
            type="submit"
            value="Enregistrer"
          />
        </div>
      </form>
    </main>
  )
}

EditEmail.propTypes = {
  redirectToPersonnalInformationPage: PropTypes.func.isRequired,
}

export default EditEmail
