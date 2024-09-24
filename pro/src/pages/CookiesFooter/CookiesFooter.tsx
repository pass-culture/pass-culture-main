import cn from 'classnames'
import React from 'react'
import { useTranslation } from 'react-i18next'

import { orejime } from 'app/App/analytics/orejime'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './CookiesFooter.module.scss'

export const CookiesFooter = ({ className }: { className?: string }) => {
  const { t } = useTranslation('common')
  const isNewSideBarNavigation = useIsNewInterfaceActive()

  if (isNewSideBarNavigation) {
    return
  }

  return (
    <footer>
      <nav>
        <ul className={cn(styles['cookies-footer'], className)}>
          <li>
            <ButtonLink
              variant={ButtonVariant.QUATERNARY}
              to="https://pass.culture.fr/cgu-professionnels/"
              isExternal
              opensInNewTab
            >
              {t('professional_terms_of_use')}
            </ButtonLink>
          </li>
          <li>
            <ButtonLink variant={ButtonVariant.QUATERNARY} to="/accessibilite">
              {t('accessibility_not_compliant')}
            </ButtonLink>
          </li>
          <li>
            <ButtonLink
              variant={ButtonVariant.QUATERNARY}
              className={styles['cookies-footer-link']}
              to="https://pass.culture.fr/donnees-personnelles/"
              isExternal
              opensInNewTab
            >
              {t('data_privacy_policy')}
            </ButtonLink>
          </li>
          <li>
            <Button
              variant={ButtonVariant.QUATERNARY}
              onClick={() => orejime.show()}
            >
              {t('cookie_management')}
            </Button>
          </li>
        </ul>
      </nav>
    </footer>
  )
}
