import React from 'react'

import TextInput from 'components/layout/inputs/TextInput/TextInput'

import styles from './ChangePasswordRequestForm.module.scss'

interface IChangePasswordRequestForm {
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void
  onSubmit: (event: React.FormEvent<HTMLFormElement>) => void
  emailValue: string
  isChangePasswordRequestSubmitDisabled: (
    values?: Record<string, string>
  ) => boolean
}

const ChangePasswordRequestForm = ({
  isChangePasswordRequestSubmitDisabled,
  emailValue,
  onSubmit,
  onChange,
}: IChangePasswordRequestForm): JSX.Element => (
  <section className={styles['change-password-request-form']}>
    <div className={styles['hero-body']}>
      <h1>Mot de passe égaré ?</h1>
      <p>
        Indiquez ci-dessous l’adresse e-mail avec laquelle vous avez créé votre
        compte.
      </p>

      <form noValidate onSubmit={onSubmit}>
        <TextInput
          label="Adresse e-mail"
          name="email"
          onChange={onChange}
          placeholder="nom@exemple.fr"
          required
          subLabel="obligatoire"
          type="email"
          value={emailValue}
        />

        <button
          className="primary-button"
          disabled={isChangePasswordRequestSubmitDisabled()}
          type="submit"
        >
          Envoyer
        </button>
      </form>
    </div>
  </section>
)

export default ChangePasswordRequestForm
