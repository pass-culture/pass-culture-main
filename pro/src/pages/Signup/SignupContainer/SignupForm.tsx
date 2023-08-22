import { useFormikContext } from 'formik'
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { ProUserCreationBodyV2Model } from 'apiClient/v1'
import { BannerRGS } from 'components/Banner'
import FormLayout from 'components/FormLayout'
import LegalInfos from 'components/LegalInfos/LegalInfos'
import CookiesFooter from 'pages/CookiesFooter/CookiesFooter'
import MaybeAppUserDialog from 'pages/Signup/SignupContainer/MaybeAppUserDialog'
import {
  Button,
  Checkbox,
  EmailSpellCheckInput,
  SubmitButton,
  TextInput,
} from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { PasswordInput } from 'ui-kit/form'
import PhoneNumberInput from 'ui-kit/form/PhoneNumberInput'

import styles from './SignupContainer.module.scss'

const SignupForm = (): JSX.Element => {
  const navigate = useNavigate()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const { isSubmitting } = useFormikContext<ProUserCreationBodyV2Model>()

  return (
    <>
      {isModalOpen && (
        <MaybeAppUserDialog onCancel={() => setIsModalOpen(false)} />
      )}

      <FormLayout>
        <FormLayout.Row>
          <TextInput label="Nom" name="lastName" autoComplete="family-name" />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextInput
            label="Prénom"
            name="firstName"
            autoComplete="given-name"
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <EmailSpellCheckInput
            name="email"
            placeholder="email@exemple.com"
            label="Adresse email"
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <PasswordInput
            name="password"
            label="Mot de passe"
            withErrorPreview={true}
            autoComplete="new-password"
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <PhoneNumberInput
            name="phoneNumber"
            label={
              'Téléphone (utilisé uniquement par l’équipe du pass Culture)'
            }
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <Checkbox
            hideFooter
            label="J’accepte d’être contacté par email pour recevoir les
                      nouveautés du pass Culture et contribuer à son
                      amélioration (facultatif)"
            name="contactOk"
          />
        </FormLayout.Row>
        <LegalInfos
          className={styles['sign-up-infos-before-signup']}
          title="Créer mon compte"
        />
        <div className={styles['buttons-field']}>
          <Button
            className={styles['buttons']}
            onClick={() => navigate('/connexion')}
            variant={ButtonVariant.SECONDARY}
          >
            J’ai déjà un compte
          </Button>
          <SubmitButton
            className={styles['buttons']}
            isLoading={isSubmitting}
            disabled={isSubmitting}
          >
            Créer mon compte
          </SubmitButton>
        </div>
        <BannerRGS />
        <CookiesFooter className={styles['cookie-footer']} />
      </FormLayout>
    </>
  )
}

export default SignupForm
