import cn from 'classnames'
import { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  GetOffererV2StatsResponseModel,
} from 'apiClient/v1'
import fullShowIcon from 'icons/full-show.svg'
import strokePhoneIcon from 'icons/stroke-phone.svg'
import strokeTeacherIcon from 'icons/stroke-teacher.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './OfferStats.module.scss'

export interface OfferStatsProps {
  offerer: GetOffererResponseModel
  className?: string
}

interface StatBlockProps {
  icon: string
  count: number
  label: string
  link: string
  linkLabel: string
}

const StatBlock = ({ icon, count, label, link, linkLabel }: StatBlockProps) => (
  <div className={styles['stat-block']}>
    <SvgIcon
      width="48"
      src={icon}
      alt=""
      className={styles['stat-block-icon']}
    />

    <div className={styles['stat-block-text']}>
      <span className={styles['stat-block-count']}>{count}</span> {label}
      <br />
      <ButtonLink
        variant={ButtonVariant.QUATERNARY}
        icon={fullShowIcon}
        link={{ to: link, isExternal: false }}
      >
        {linkLabel}
      </ButtonLink>
    </div>
  </div>
)

export const OfferStats = ({ offerer, className }: OfferStatsProps) => {
  const [stats, setStats] = useState<GetOffererV2StatsResponseModel | null>(
    null
  )
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    const loadStats = async () => {
      setIsLoading(true)
      const response = await api.getOffererV2Stats(offerer.id)
      setStats(response)
      setIsLoading(false)
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadStats()
  }, [offerer.id])

  return (
    <div className={cn(className, 'h-card')}>
      <div className="h-card-inner">
        <h3 className={styles['title']}>Vos offres publiées</h3>

        <div className={styles['container']}>
          {isLoading || stats === null ? (
            <>
              <div className={styles['skeleton']} />
              <div className={styles['skeleton']} />
            </>
          ) : (
            <>
              <StatBlock
                icon={strokePhoneIcon}
                count={stats.publishedPublicOffers}
                label="à destination du grand public"
                link={`/offres?structure=${offerer.id}&status=active`}
                linkLabel="Voir les offres individuelles publiées"
              />

              <StatBlock
                icon={strokeTeacherIcon}
                count={stats.publishedEducationalOffers}
                label="à destination de groupes scolaires"
                link=""
                linkLabel="Voir les offres collectives publiées"
              />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
