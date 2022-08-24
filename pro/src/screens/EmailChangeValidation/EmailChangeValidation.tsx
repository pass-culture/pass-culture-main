// react hooks and usages doc : https://reactjs.org/docs/hooks-intro.html
import React from 'react'

import Logo from 'components/layout/Logo'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

interface IEmailChangeValidationProps {
  isSuccess: boolean
}

const EmailChangeValidation = ({
  isSuccess,
}: IEmailChangeValidationProps): JSX.Element => {
  return (
    <>
      <div className="logo-side">
        <Logo noLink signPage />
      </div>
      <div className="scrollable-content-side">
        <div className="content" id="override-content-width">
          {isSuccess && (
            <section className="password-set-request-form">
              <div>
                <h1>Et voilà !</h1>
                <h2>
                  Merci d’avoir confirmé votre changement d’adresse e-mail.
                </h2>
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
            <section className="password-set-request-form">
              <div>
                <h1>Votre lien a expiré !</h1>
                <h2>
                  Votre adresse e-mail n’a pas été modifiée car le lien reçu par
                  mail expire 24 heures après sa récéption.
                </h2>
                <h2>Connectez-vous avec votre ancienne adresse e-mail.</h2>
                <ButtonLink
                  variant={ButtonVariant.PRIMARY}
                  link={{ to: '/', isExternal: false }}
                >
                  Se connecter
                </ButtonLink>
              </div>
            </section>
          )}
        </div>
      </div>
    </>
  )
}

export default EmailChangeValidation
