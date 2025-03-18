import cn from 'classnames'
import { useId } from 'react'
import { useFormContext } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'

import { ProUserCreationBodyV2Model } from 'apiClient/v1'
import { parseAndValidateFrenchPhoneNumber } from 'commons/core/shared/utils/parseAndValidateFrenchPhoneNumber'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useMediaQuery } from 'commons/hooks/useMediaQuery'
import { BannerRGS } from 'components/BannerRGS/BannerRGS'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { LegalInfos } from 'components/LegalInfos/LegalInfos'
import { ScrollToFirstHookFormErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import iconFullNext from 'icons/full-next.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
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
  const isNewSignupEnabled = useActiveFeature('WIP_2025_SIGN_UP')
  const isLaptopScreenAtLeast = useMediaQuery('(min-width: 64rem)')
  const formId = useId()

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

      <FormLayout>
        <div
          className={cn({
            [styles['signup-form-row']]: isNewSignupEnabled,
          })}
        >
          {[
            <FormLayout.Row
              key={`${formId}-lastName`}
              className={cn({
                [styles['signup-form-group']]: isNewSignupEnabled,
              })}
            >
              <TextInput
                label="Nom"
                {...register('lastName')}
                error={errors.lastName?.message}
                autoComplete="family-name"
                required
                asterisk={!isNewSignupEnabled}
              />
            </FormLayout.Row>,
            <FormLayout.Row
              key={`${formId}-firstName`}
              className={cn({
                [styles['signup-form-group']]: isNewSignupEnabled,
              })}
            >
              <TextInput
                label="Prénom"
                {...register('firstName')}
                error={errors.firstName?.message}
                autoComplete="given-name"
                required
                asterisk={!isNewSignupEnabled}
              />
            </FormLayout.Row>,
          ].toSorted(() => (isNewSignupEnabled ? -1 : 1))}
          {/* This is to display fields "PRÉNOM" <> "NOM" in the correct DOM order depending on the FF */}
        </div>
        <FormLayout.Row>
          <EmailSpellCheckInput
            {...register('email')}
            error={errors.email?.message}
            onApplyTip={(tip) => {
              setValue('email', tip)
            }}
            description="Format : email@exemple.com"
            label="Adresse email"
            required
            asterisk={!isNewSignupEnabled}
          />
        </FormLayout.Row>
        <FormLayout.Row className={styles['signup-form-row-password']}>
          <PasswordInput
            {...register('password')}
            label="Mot de passe"
            autoComplete="new-password"
            required
            asterisk={!isNewSignupEnabled}
          />
          <ValidationMessageList
            passwordValue={newPassword}
            hasError={!!errors.password}
          />
        </FormLayout.Row>
        {!isNewSignupEnabled && (
          <FormLayout.Row>
            <PhoneNumberInput
              {...register('phoneNumber', {
                onBlur(event) {
                  // This is because entries like "+33600110011invalid" are considered valid by libphonenumber-js,
                  // We need to explicitely extract "+33600110011" that is in the .number property
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
              label={'Téléphone (utilisé uniquement par le pass Culture)'}
              required
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
        {isNewSignupEnabled ? (
          <>
            <div className={styles['buttons-field']}>
              <Button
                type="submit"
                className={styles['buttons']}
                isLoading={isSubmitting}
                disabled={isSubmitting}
              >
                S’inscrire
              </Button>
            </div>
            <aside className={styles['no-account']}>
              <p className={styles['no-account-text']}>
                Vous avez déjà un compte ?
              </p>
              <ButtonLink
                to="/connexion"
                icon={iconFullNext}
                variant={
                  isLaptopScreenAtLeast
                    ? ButtonVariant.TERNARY
                    : ButtonVariant.QUATERNARY
                }
              >
                Se connecter
              </ButtonLink>
            </aside>
          </>
        ) : (
          <>
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
          </>
        )}
      </FormLayout>
    </>
  )
}
