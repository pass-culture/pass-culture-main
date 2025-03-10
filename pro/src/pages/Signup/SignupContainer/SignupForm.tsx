import { useState } from 'react'
import { useFormContext } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'

import { ProUserCreationBodyV2Model } from 'apiClient/v1'
import { parseAndValidateFrenchPhoneNumber } from 'commons/core/shared/utils/parseAndValidateFrenchPhoneNumber'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { BannerRGS } from 'components/BannerRGS/BannerRGS'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { LegalInfos } from 'components/LegalInfos/LegalInfos'
import { ScrollToFirstHookFormErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { MaybeAppUserDialog } from 'pages/Signup/SignupContainer/MaybeAppUserDialog/MaybeAppUserDialog'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Checkbox } from 'ui-kit/formV2/Checkbox/Checkbox'
import { EmailSpellCheckInput } from 'ui-kit/formV2/EmailSpellCheckInput/EmailSpellCheckInput'
import { PasswordInput } from 'ui-kit/formV2/PasswordInput/PasswordInput'
import { PhoneNumberInput } from 'ui-kit/formV2/PhoneNumberInput/PhoneNumberInput'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'
import { ValidationMessageList } from 'ui-kit/formV2/ValidationMessageList/ValidationMessageList'

import styles from './SignupContainer.module.scss'

export const SignupForm = (): JSX.Element => {
  const navigate = useNavigate()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const isNewSignupEnabled = useActiveFeature('WIP_2025_SIGN_UP')

  const {
    formState: { isSubmitting, errors },
    register,
    watch,
    setValue,
  } = useFormContext<ProUserCreationBodyV2Model>()

  const newPassword = watch('password')

  return (
    <>
      <ScrollToFirstHookFormErrorAfterSubmit />

      <MaybeAppUserDialog
        onCancel={() => setIsModalOpen(false)}
        isDialogOpen={isModalOpen}
      />

      <FormLayout>
        <FormLayout.Row>
          <TextInput
            label="Nom"
            {...register('lastName')}
            error={errors.lastName?.message}
            autoComplete="family-name"
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextInput
            label="Prénom"
            {...register('firstName')}
            error={errors.firstName?.message}
            autoComplete="given-name"
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <EmailSpellCheckInput
            {...register('email')}
            error={errors.email?.message}
            onApplyTip={(tip) => {
              setValue('email', tip)
            }}
            description="Format : email@exemple.com"
            label="Adresse email"
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <PasswordInput
            {...register('password')}
            error={errors.password?.message}
            label="Mot de passe"
            autoComplete="new-password"
          />
          <ValidationMessageList passwordValue={newPassword} />
        </FormLayout.Row>
        {!isNewSignupEnabled && (
          <FormLayout.Row>
            <PhoneNumberInput
              {...register('phoneNumber', {
                onBlur(event) {
                  // Temporary : This is to stick with the current behavior that strips the invalid part of a valid number
                  //  ex: "+33600110011invalid" -> "+33600110011"
                  // but this should be discussed because "+33600110011invalid" should be considered as invalid !
                  try {
                    const phoneNumber = parseAndValidateFrenchPhoneNumber(
                      event.target.value
                    ).number
                    setValue('phoneNumber', phoneNumber)
                    // eslint-disable-next-line @typescript-eslint/no-unused-vars
                  } catch (e) {
                    // phone is considered invalid by the lib, so we does nothing here and let yup indicates the error
                  }
                },
              })}
              error={errors.phoneNumber?.message}
              name="phoneNumber"
              label={
                'Téléphone (utilisé uniquement par l’équipe du pass Culture)'
              }
            />
          </FormLayout.Row>
        )}
        <FormLayout.Row>
          <Checkbox
            className={styles['checkbox-contact']}
            hideFooter
            label="J’accepte d’être contacté par email pour recevoir les
                      nouveautés du pass Culture et contribuer à son
                      amélioration (facultatif)"
            {...register('contactOk')}
            error={errors.contactOk?.message}
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
      </FormLayout>
    </>
  )
}
