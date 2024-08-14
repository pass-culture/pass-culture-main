import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

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

  const formattedData = dailyViews.map((dailyView) => ({
    date: new Date(dailyView.eventDate).getTime() || 0,
    views: dailyView.numberOfViews || 0,
  }))

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
              to="https://passcultureapp.notion.site/Les-bonnes-pratiques-et-tudes-du-pass-Culture-323b1a0ec309406192d772e7d803fbd0"
              isExternal
              opensInNewTab
              variant={ButtonVariant.TERNARY}
              icon={fullLinkIcon}
            >
              Bonnes pratiques de création d’offres
            </ButtonLink>
          </div>
        </div>
      ) : (
        <div className={styles['chart']}>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart
              data={formattedData}
              margin={{ top: 0, right: 0, left: 0, bottom: 16 }}
            >
              <CartesianGrid />
              <XAxis
                label={{
                  value: 'Date',
                  position: 'bottom',
                }}
                dataKey="date"
                type="number"
                scale="time"
                domain={['auto', 'auto']}
                tickFormatter={(tick) =>
                  new Date(tick).toLocaleDateString('fr-FR', {
                    year: 'numeric',
                    month: 'numeric',
                    day: 'numeric',
                  })
                }
              />
              <YAxis
                label={{
                  value: 'Nombre de vues cumulées',
                  angle: -90,
                  dx: -20,
                }}
                offset={10000}
                // dx={-20}
                // scaleToFit
              />
              <Tooltip
                labelFormatter={(label) =>
                  new Date(label).toLocaleDateString('fr-FR', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                  })
                }
              />
              <Line
                type="monotone"
                dataKey="views"
                stroke={chartColors.primary}
                strokeWidth={3}
              />
            </LineChart>
          </ResponsiveContainer>

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
