import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './ErrorLayout.module.scss'

interface ErrorLayoutProps {
  /**
   * Name of the page to display in the main heading.
   * Make sure that only one heading is displayed per page.
   */
  mainHeading: React.ReactNode
  /**
   * Description paragraph to display below the main heading.
   */
  paragraph: string
  /**
   * Icon to display in the error page.
   */
  errorIcon: string
  /**
   * Redirect link for the button.
   */
  redirect?: string
}

export const ErrorLayout = ({
  mainHeading,
  paragraph,
  errorIcon,
  redirect = '/accueil',
}: ErrorLayoutProps) => {
  return (
    <main className={styles['content-wrapper']}>
      <div className={styles['content']}>
        <SvgIcon className={styles['error-icon']} src={errorIcon} alt="" />
        <h1 className={styles['title']}>{mainHeading}</h1>
        <p className={styles.description}>{paragraph}</p>
        <ButtonLink
          className={styles['nm-redirection-link']}
          variant={ButtonVariant.SECONDARY}
          to={redirect}
        >
          Retour à la page d’accueil
        </ButtonLink>
      </div>
    </main>
  )
}
