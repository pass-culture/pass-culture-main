import cn from 'classnames'
import { useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'

import styles from './LegalInfos.module.scss'

interface LegalInfoProps {
  className: string
}

export const LegalInfos = ({ className }: LegalInfoProps): JSX.Element => {
  const location = useLocation()
  const { logEvent } = useAnalytics()

  const DPOMail = 'dpo@passculture.app'

  return (
    <div className={cn(styles['legal-infos-callout'], className)}>
      <Banner
        title="Acceptation des conditions et protection des données"
        description={
          <>
            <p className={styles['legal-infos-paragraph']}>
              En cliquant sur S’inscrire, vous acceptez nos{' '}
              <Button
                as="a"
                variant={ButtonVariant.TERTIARY}
                color={ButtonColor.NEUTRAL}
                size={ButtonSize.SMALL}
                icon={fullLinkIcon}
                opensInNewTab
                isExternal
                onClick={() =>
                  logEvent(Events.CLICKED_CONSULT_CGU, {
                    from: location.pathname,
                  })
                }
                to="https://pass.culture.fr/cgu-professionnels/"
                label="Conditions générales d’utilisation."
              />
            </p>
            <p className={styles['legal-infos-paragraph']}>
              Pour la gestion de vos données personnelles par la SAS pass
              Culture, vous pouvez consulter la{' '}
              <Button
                as="a"
                icon={fullLinkIcon}
                variant={ButtonVariant.TERTIARY}
                color={ButtonColor.NEUTRAL}
                size={ButtonSize.SMALL}
                isExternal
                opensInNewTab
                to="https://pass.culture.fr/donnees-personnelles/"
                label="charte des données personnelles"
              />
            </p>
            <p>
              ou contacter{' '}
              <Button
                as="a"
                variant={ButtonVariant.TERTIARY}
                color={ButtonColor.NEUTRAL}
                size={ButtonSize.SMALL}
                icon={fullLinkIcon}
                to={`mailto:${DPOMail}`}
                isExternal
                label={DPOMail}
              />
              .
            </p>
          </>
        }
      />
    </div>
  )
}
