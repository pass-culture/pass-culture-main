import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
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
  redirect = '/',
}: ErrorLayoutProps) => {
  const currentUser = useAppSelector(selectCurrentUser)
  const isConnected = !!currentUser

  return (
    <main className={styles['content-wrapper']}>
      <div className={styles['content']}>
        <SvgIcon className={styles['error-icon']} src={errorIcon} alt="" />
        <h1 className={styles['title']}>{mainHeading}</h1>
        <p className={styles.description}>{paragraph}</p>
        <div className={styles['nm-redirection-link']}>
          {/** biome-ignore lint/correctness/useUniqueElementIds: This is always
          rendered once per page, so there cannot be id duplications.> */}
          <Button
            as="a"
            id="error-return-link"
            variant={ButtonVariant.SECONDARY}
            to={redirect}
            label={isConnected ? "Retour à la page d'accueil" : 'Retour'}
          />
        </div>
      </div>
    </main>
  )
}
