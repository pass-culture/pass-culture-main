import { useFormikContext } from 'formik'
import React, { useState } from 'react'
import { useHistory } from 'react-router-dom'

import { BannerInvisibleSiren, BannerRGS } from 'components/Banner'
import FormLayout from 'components/FormLayout'
import LegalInfos from 'components/LegalInfos/LegalInfos'
import { getSirenDataAdapter } from 'core/Offerers/adapters'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import { useModal } from 'hooks/useModal'
import { Button, SubmitButton, TextInput, Checkbox } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { PasswordInput, SirenInput } from 'ui-kit/form'
import PhoneNumberInput from 'ui-kit/form/PhoneNumberInput'

import { MAYBE_APP_USER_APE_CODE } from './constants'
import styles from './SignupContainer.module.scss'
import { ISignupFormValues } from './types'

const SignupForm = (): JSX.Element => {
  const history = useHistory()
  const [showAnonymousBanner, setShowAnonymousBanner] = useState(false)
  const { showModal } = useModal()
  const { values, setFieldValue, setFieldError, isSubmitting } =
    useFormikContext<ISignupFormValues>()

  useScrollToFirstErrorAfterSubmit()

  const getSirenAPIData = async (siren: string) => {
    setShowAnonymousBanner(false)
    const response = await getSirenDataAdapter(siren)
    if (response.isOk) {
      let values = undefined
      if (response.payload.values != null) {
        const { apeCode, ...rest } = response.payload.values
        values = rest
        if (MAYBE_APP_USER_APE_CODE.includes(apeCode)) {
          showModal()
        }
      }

      setFieldValue('legalUnitValues', values)
    } else {
      setFieldError('siren', response.message)
      if (
        response.message ==
        'Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles.'
      ) {
        setShowAnonymousBanner(true)
      }
    }
  }

  return (
    <FormLayout>
      <div className={styles['sign-up-form']}>
        <FormLayout.Row>
          <TextInput
            label="Adresse e-mail"
            name="email"
            placeholder="mail@exemple.com"
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <PasswordInput
            name="password"
            label="Mot de passe"
            placeholder="Votre mot de passe"
            withErrorPreview={true}
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextInput label="Nom" name="lastName" placeholder="Votre nom" />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextInput
            label="Prénom"
            name="firstName"
            placeholder="Votre prénom"
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
        <div className={styles['siren-field']}>
          <FormLayout.Row>
            <SirenInput
              label="SIREN de la structure que vous représentez"
              onValidSiren={getSirenAPIData}
            />
          </FormLayout.Row>
          <span className={styles['field-siren-value']}>
            {values.legalUnitValues.name}
          </span>
          {showAnonymousBanner && <BannerInvisibleSiren />}
        </div>
        <FormLayout.Row>
          <Checkbox
            hideFooter
            label="J’accepte d’être contacté par e-mail pour recevoir les
                      nouveautés du pass Culture et contribuer à son
                      amélioration (facultatif)"
            name="contactOk"
          />
        </FormLayout.Row>
        <LegalInfos
          className={styles['sign-up-infos-before-signup']}
          title="Créer mon compte"
        />
      </div>
      <div className={styles['buttons-field']}>
        <Button
          onClick={() => history.push('/connexion')}
          variant={ButtonVariant.SECONDARY}
        >
          J’ai déjà un compte
        </Button>
        <SubmitButton isLoading={isSubmitting} disabled={isSubmitting}>
          Créer mon compte
        </SubmitButton>
      </div>
      <BannerRGS />
    </FormLayout>
  )
}

export default SignupForm
