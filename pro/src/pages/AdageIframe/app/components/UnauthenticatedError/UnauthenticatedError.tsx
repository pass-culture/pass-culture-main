import logoPassCultureIcon from 'icons/logo-pass-culture.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './UnauthenticatedError.module.scss'

export function UnauthenticatedError(): JSX.Element {
  return (
    <main className={styles['error']} id="content">
      <div className={styles['error-header']}>
        <div className={styles['error-header-brand']}>
          <SvgIcon
            src={logoPassCultureIcon}
            alt="pass Culture"
            width="109"
            viewBox="0 0 71 24"
          />
        </div>
      </div>
      <div className={styles['error-content']}>
        <h1 className={styles['error-content-title']}>
          Une erreur s’est produite
        </h1>
      </div>
    </main>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = UnauthenticatedError
