import { fr } from 'date-fns/locale'
import React from 'react'
import { Line } from 'react-chartjs-2'

import { OffererViewsModel } from 'apiClient/v1'
import fullLinkIcon from 'icons/full-link.svg'
import strokeBookingHoldIcon from 'icons/stroke-booking-hold.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { chartColors } from 'ui-kit/chartGlobals'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './CumulatedViews.module.scss'

export interface CumulatedViewsProps {
  dailyViews: OffererViewsModel[]
}

export const CumulatedViews = ({ dailyViews }: CumulatedViewsProps) => {
  const hasNoViews =
    dailyViews.length < 2 ||
    dailyViews.every((view) => view.numberOfViews === 0)

  const data = {
    datasets: [
      {
        data: dailyViews.map((dailyView) => ({
          x: dailyView.eventDate,
          y: dailyView.numberOfViews,
        })),
        pointStyle: false as const,
        backgroundColor: chartColors.primary,
        borderColor: chartColors.primary,
        tension: 0.3,
      },
    ],
  }

  const options = {
    scales: {
      x: {
        title: { display: true, text: 'Date' },
        type: 'time',
        adapters: { date: { locale: fr } },
      },
      y: {
        title: { display: true, text: 'Nombre de vues cumulées' },
      },
    },
  } as const

  return (
    <div className={styles['cumulated-views']}>
      <div>
        <h3 className={styles['block-title']}>
          Évolution des consultations de vos offres
        </h3>
        <span>ces 6 derniers mois</span>
      </div>

      {hasNoViews ? (
        <div className={styles['no-data']}>
          <SvgIcon
            className={styles['no-data-icon']}
            src={strokeBookingHoldIcon}
            alt=""
            width="128"
          />

          <div className={styles['no-data-caption']}>
            Vos offres n’ont pas encore été découvertes par les bénéficiaires
          </div>

          <div>
            Inspirez-vous des conseils de nos équipes pour améliorer la
            visibilité de vos offres
          </div>

          <div>
            <ButtonLink
              link={{
                to: 'https://passcultureapp.notion.site/Les-bonnes-pratiques-et-tudes-du-pass-Culture-323b1a0ec309406192d772e7d803fbd0',
                isExternal: true,
                target: '_blank',
              }}
              svgAlt="Nouvelle fenêtre"
              variant={ButtonVariant.TERNARY}
              icon={fullLinkIcon}
            >
              Bonnes pratiques de création d’offres
            </ButtonLink>
          </div>
        </div>
      ) : (
        <div className={styles['chart']}>
          <Line
            data={data}
            options={options}
            role="img"
            aria-labelledby="chart-title"
            aria-details="chart-description"
          />

          {/* Wrap in visually hidden div, this class doesn't work on Chrome on <table> element */}
          <div className="visually-hidden">
            <table id="chart-description">
              <caption id="chart-title">
                Nombre de vues cumulées de toutes vos offres sur les 6 derniers
                mois
              </caption>

              <thead>
                <tr>
                  <th scope="col">Date</th>
                  <th scope="col">Nombre de vues cumulées</th>
                </tr>
              </thead>
              <tbody>
                {dailyViews.map((dailyView) => (
                  <tr key={dailyView.eventDate}>
                    <td>{dailyView.eventDate}</td>
                    <td>{dailyView.numberOfViews}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
