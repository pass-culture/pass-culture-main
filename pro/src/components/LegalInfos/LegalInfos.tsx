import cn from 'classnames'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { Banner } from '@/design-system/Banner/Banner'
import { Link } from '@/design-system/Link/Link'
import { LinkColor, LinkSize } from '@/design-system/Link/types'

import styles from './LegalInfos.module.scss'

interface LegalInfoProps {
  className: string
}

export const LegalInfos = ({ className }: LegalInfoProps): JSX.Element => {
  const { logEvent } = useAnalytics()

  const DPOMail = 'dpo@passculture.app'

  return (
    <div className={cn(styles['legal-infos-callout'], className)}>
      <Banner
        title="Acceptation des conditions et protection des données"
        description={
          <p className={styles['legal-infos-paragraph']}>
            En cliquant sur S’inscrire, vous acceptez nos{' '}
            <Link
              color={LinkColor.NEUTRAL}
              size={LinkSize.SMALL}
              shouldOpenNewTab
              isExternalLink
              onClick={() => logEvent(Events.CLICKED_CONSULT_CGU)}
              to="https://pass.culture.fr/cgu-professionnels/"
              label="Conditions générales d’utilisation"
            />
            . Pour la gestion de vos données personnelles par la SAS pass
            Culture, vous pouvez consulter la{' '}
            <Link
              color={LinkColor.NEUTRAL}
              size={LinkSize.SMALL}
              shouldOpenNewTab
              isExternalLink
              to="https://pass.culture.fr/donnees-personnelles/"
              label="charte des données personnelles"
            />{' '}
            ou contacter{' '}
            <Link
              color={LinkColor.NEUTRAL}
              size={LinkSize.SMALL}
              shouldOpenNewTab
              isExternalLink
              to={`mailto:${DPOMail}`}
              label={DPOMail}
            />
            .
          </p>
        }
      />
    </div>
  )
}
