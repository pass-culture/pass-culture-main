// react hooks and usages doc : https://reactjs.org/docs/hooks-intro.html
import React from 'react'

import logoPassCultureProFullIcon from 'icons/logo-pass-culture-pro-full.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './EmailChangeValidation.module.scss'

interface EmailChangeValidationProps {
  isSuccess: boolean
}

export const EmailChangeValidationScreen = ({
  isSuccess,
}: EmailChangeValidationProps): JSX.Element => {
  return (
    <>
      <header className={styles['logo-side']}>
        <SvgIcon
          className="logo-unlogged"
          viewBox="0 0 282 120"
          alt="Pass Culture pro, l’espace des acteurs culturels"
          src={logoPassCultureProFullIcon}
          width="135"
        />
      </header>
      {isSuccess && (
        <section className={styles['content']}>
          <h1 className={styles['title']}>Et voilà !</h1>
          <p className={styles['subtitle']}>
            Merci d’avoir confirmé votre changement d’adresse email.
          </p>
          <ButtonLink variant={ButtonVariant.PRIMARY} to="/">
            Se connecter
          </ButtonLink>
        </section>
      )}
      {!isSuccess && (
        <section className={styles['content']}>
          <h1 className={styles['title']}>Votre lien a expiré !</h1>
          <p className={styles['subtitle']}>
            Votre adresse email n’a pas été modifiée car le lien reçu par mail
            expire 24 heures après sa réception.
          </p>
          <p className={styles['subtitle']}>
            Connectez-vous avec votre ancienne adresse email.
          </p>
          <ButtonLink variant={ButtonVariant.PRIMARY} to="/">
            Se connecter
          </ButtonLink>
        </section>
      )}
    </>
  )
}
