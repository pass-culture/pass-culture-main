// react hooks and usages doc : https://reactjs.org/docs/hooks-intro.html
import React from 'react'

import AppLayout from 'app/AppLayout'
import SkipLinks from 'components/SkipLinks'
import logoPassCultureProFullIcon from 'icons/logo-pass-culture-pro-full.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './EmailChangeValidation.module.scss'

interface EmailChangeValidationProps {
  isSuccess: boolean
}

const EmailChangeValidation = ({
  isSuccess,
}: EmailChangeValidationProps): JSX.Element => {
  return (
    <>
      <SkipLinks displayMenu={false} />
      <div className={styles['email-validation']}>
        <header className={styles['logo-side']}>
          <SvgIcon
            className="logo-unlogged"
            viewBox="0 0 282 120"
            alt="Pass Culture pro, l'espace des acteurs culturels"
            src={logoPassCultureProFullIcon}
          />
        </header>
        <AppLayout
          layoutConfig={{
            fullscreen: true,
            pageName: 'sign-up',
          }}
        >
          {isSuccess && (
            <section className={styles['scrollable-content-side']}>
              <div>
                <h1>Et voilà !</h1>
                <p className={styles['search-no-results-title4']}>
                  Merci d’avoir confirmé votre changement d’adresse email.
                </p>
                <ButtonLink
                  variant={ButtonVariant.PRIMARY}
                  link={{ to: '/', isExternal: false }}
                >
                  Se connecter
                </ButtonLink>
              </div>
            </section>
          )}
          {!isSuccess && (
            <section className={styles['scrollable-content-side']}>
              <div>
                <h1>Votre lien a expiré !</h1>
                <p className={styles['search-no-results-title4']}>
                  Votre adresse email n’a pas été modifiée car le lien reçu par
                  mail expire 24 heures après sa réception.
                </p>
                <p className={styles['search-no-results-title4']}>
                  Connectez-vous avec votre ancienne adresse email.
                </p>
                <ButtonLink
                  variant={ButtonVariant.PRIMARY}
                  link={{ to: '/', isExternal: false }}
                >
                  Se connecter
                </ButtonLink>
              </div>
            </section>
          )}
        </AppLayout>
      </div>
    </>
  )
}

export default EmailChangeValidation
