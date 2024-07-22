import { useFormikContext } from 'formik'
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { ProUserCreationBodyV2Model } from 'apiClient/v1'
import { BannerRGS } from 'components/Banner/BannerRGS'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { LegalInfos } from 'components/LegalInfos/LegalInfos'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { CookiesFooter } from 'pages/CookiesFooter/CookiesFooter'
import { MaybeAppUserDialog } from 'pages/Signup/SignupContainer/MaybeAppUserDialog/MaybeAppUserDialog'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Checkbox } from 'ui-kit/form/Checkbox/Checkbox'
import { EmailSpellCheckInput } from 'ui-kit/form/EmailSpellCheckInput/EmailSpellCheckInput'
import { PasswordInput } from 'ui-kit/form/PasswordInput/PasswordInput'
import { PhoneNumberInput } from 'ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './SignupContainer.module.scss'

export const SignupForm = (): JSX.Element => {
  const navigate = useNavigate()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const { isSubmitting } = useFormikContext<ProUserCreationBodyV2Model>()

  return (
    <>
      <ScrollToFirstErrorAfterSubmit />

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
            className={styles['checkbox-contact']}
            hideFooter
            label="J’accepte d’être contacté par email pour recevoir les
                      nouveautés du pass Culture et contribuer à son
                      amélioration (facultatif)"
            name="contactOk"
          />
        </FormLayout.Row>
        <LegalInfos
          className={styles['sign-up-infos-before-signup'] ?? ''}
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
          <Button
            type="submit"
            className={styles['buttons']}
            isLoading={isSubmitting}
            disabled={isSubmitting}
          >
            Créer mon compte
          </Button>
        </div>
        <BannerRGS />
        <CookiesFooter className={styles['cookie-footer']} />
      </FormLayout>
    </>
  )
}
