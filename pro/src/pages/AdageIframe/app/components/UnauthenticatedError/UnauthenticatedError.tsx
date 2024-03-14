import logoPassCultureIcon from 'icons/logo-pass-culture.svg'
import { ButtonLink } from 'ui-kit'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './UnauthenticatedError.module.scss'

export default function UnauthenticatedError(): JSX.Element {
  return (
    <main className={styles['error']} id="content">
      <div className={styles['error-header']}>
        <div className={styles['error-header-brand']}>
          <SvgIcon
            src={logoPassCultureIcon}
            alt="Logo du pass Culture"
            width="109"
            viewBox="0 0 71 24"
          />
        </div>
      </div>
      <div className={styles['error-content']}>
        <h1 className={styles['error-content-title']}>
          Une erreur s’est produite
        </h1>
        <p>
          Contactez{' '}
          <ButtonLink
            link={{
              isExternal: true,
              to: 'mailto:adage-pass-culture@education.gouv.fr',
            }}
          >
            adage-pass-culture@education.gouv.fr
          </ButtonLink>{' '}
          pour obtenir de l’aide.
        </p>
      </div>
    </main>
  )
}
