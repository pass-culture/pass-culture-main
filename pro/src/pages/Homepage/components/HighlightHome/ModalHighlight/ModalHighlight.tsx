import type { ReactNode } from 'react'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_HIGHLIGHTS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { EngagementEvents } from '@/commons/core/FirebaseEvents/constants'
import { HighlightDatespanTag } from '@/components/HighlightDatespanTag/HighlightDatespanTag'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { DetailedModal } from '@/design-system/DetailedModal/DetailedModal'
import { Tag } from '@/design-system/Tag/Tag'
import { AccessibleDate } from '@/ui-kit/AccessibleDate/AccessibleDate'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './ModalHighlight.module.scss'

interface ModalHighlightProps {
  isOpen: boolean
  onClose: () => void
}

export const ModalHighlight = ({
  isOpen,
  onClose,
}: ModalHighlightProps): JSX.Element | null => {
  const { logEvent } = useAnalytics()
  const { data, isLoading } = useSWR([GET_HIGHLIGHTS_QUERY_KEY], () =>
    api.getHighlights()
  )

  return (
    <DetailedModal
      isOpen={isOpen}
      onClose={onClose}
      title="Qu’est-ce qu’un temps fort sur le pass Culture ?"
      primaryAction={
        <Button
          as="router-link"
          to="/offres"
          variant={ButtonVariant.PRIMARY}
          onClick={() =>
            logEvent(EngagementEvents.HAS_REQUESTED_HIGHLIGHTS, {
              action: 'goToOffersList',
            })
          }
          label="Accéder à mes offres"
        />
      }
      secondaryAction={
        <Button
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          onClick={onClose}
          label="Fermer"
        />
      }
    >
      <div>
        <p>
          C’est une valorisation de vos évènements via un temps fort thématique.
          Elle pourra se faire sur l’application et dans nos communications aux
          jeunes (newsletters, notifications, sélections, page d’accueil).
        </p>
        <div className={styles['callout']}></div>
        <Banner
          title="Comment participer ?"
          description={
            <ul>
              <li>
                - Créez votre offre d’évènement ou choisissez en une dans votre
                liste d’offres
              </li>
              <li>- Ouvrez votre offre</li>
              <li>- Choisissez le temps fort</li>
            </ul>
          }
        />
        {isLoading ? (
          <Spinner />
        ) : (
          <>
            <h2 className={styles['highlight-title']}>
              Les prochains temps forts :{' '}
            </h2>
            <ul className={styles['cards-container']}>
              {data?.map(
                ({
                  id,
                  description,
                  mediationUrl,
                  name,
                  communicationDate,
                  highlightDatespan,
                }) => (
                  <li key={id}>
                    <HighlightCard
                      imageSrc={mediationUrl}
                      title={name}
                      communicationDate={communicationDate}
                      highlightDatespan={highlightDatespan}
                    >
                      {description}
                    </HighlightCard>
                  </li>
                )
              )}
            </ul>
          </>
        )}
        <div className={styles['links-container']}>
          <Button
            as="a"
            to="https://aide.passculture.app/hc/fr/articles/20587966046748--Acteurs-Culturels-Comment-et-pourquoi-proposer-des-offres-dans-le-cadre-des-temps-forts-et-zooms-th%C3%A9matiques"
            opensInNewTab
            onClick={() =>
              logEvent(EngagementEvents.HAS_REQUESTED_HIGHLIGHTS, {
                action: 'seeMoreInfo',
              })
            }
            label="En savoir plus sur les temps forts"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
          />
          <Button
            as="a"
            to="https://passcultureapp.notion.site/1cfad4e0ff9880288df4c80eebfe3ca0?v=1cfad4e0ff9880f3bbfd000c6f5023f3"
            opensInNewTab
            onClick={() =>
              logEvent(EngagementEvents.HAS_REQUESTED_HIGHLIGHTS, {
                action: 'seeCalendar',
              })
            }
            label="Voir tout le calendrier"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
          />
        </div>
      </div>
    </DetailedModal>
  )
}

type HighlightCardProps = {
  imageSrc: string
  title: ReactNode
  children: ReactNode
  communicationDate: string
  highlightDatespan: string[]
}

const HighlightCard = ({
  imageSrc,
  title,
  children,
  communicationDate,
  highlightDatespan,
}: HighlightCardProps) => {
  const limitDate = new Date(communicationDate)
  limitDate.setDate(limitDate.getDate() - 5)

  return (
    <div className={styles['card']}>
      <div className={styles['card-content']}>
        <img src={imageSrc} alt="" className={styles['card-image']} />
        <Tag
          label={<HighlightDatespanTag highlightDatespan={highlightDatespan} />}
        />
        <h3 className={styles['card-title']}>{title}</h3>
        <p className={styles['card-description']}>{children}</p>
        <p className={styles['card-limit-participation-date']}>
          Date limite de participation : <AccessibleDate date={limitDate} />
        </p>
      </div>
    </div>
  )
}
