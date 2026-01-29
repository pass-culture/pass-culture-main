import * as Dialog from '@radix-ui/react-dialog'
import type { ReactNode } from 'react'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_HIGHLIGHTS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { HighlightEvents } from '@/commons/core/FirebaseEvents/constants'
import { HighlightDatespanTag } from '@/components/HighlightDatespanTag/HighlightDatespanTag'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Tag } from '@/design-system/Tag/Tag'
import fullLinkIcon from '@/icons/full-link.svg'
import { AccessibleDate } from '@/ui-kit/AccessibleDate/AccessibleDate'
import {
  DialogBuilder,
  type DialogBuilderProps,
} from '@/ui-kit/DialogBuilder/DialogBuilder'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './ModalHighlight.module.scss'

interface ModalHighlight extends Omit<DialogBuilderProps, 'children'> {}

export const ModalHighlight = ({
  ...dialogBuilderProps
}: ModalHighlight): JSX.Element | null => {
  const { logEvent } = useAnalytics()
  const { data, isLoading } = useSWR([GET_HIGHLIGHTS_QUERY_KEY], () =>
    api.getHighlights()
  )

  return (
    <DialogBuilder
      {...dialogBuilderProps}
      title="Qu’est-ce qu’un temps fort sur le pass Culture ?"
      variant="drawer"
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
            {/* biome-ignore lint/a11y/useSemanticElements: correct voiceover bug with list displayed with flex
            biome-ignore lint/a11y/noRedundantRoles: idem */}
            <ul className={styles['cards-container']} role="list">
              {data?.map(
                ({
                  id,
                  description,
                  mediationUrl,
                  name,
                  communicationDate,
                  highlightDatespan,
                }) => (
                  // biome-ignore lint/a11y/useSemanticElements: correct voiceover bug with list displayed with flex
                  // biome-ignore lint/a11y/noRedundantRoles: idem
                  <li key={id} role="listitem">
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
      </div>
      <div className={styles['links-container']}>
        <Button
          as="a"
          to="https://aide.passculture.app/hc/fr/articles/20587966046748--Acteurs-Culturels-Comment-et-pourquoi-proposer-des-offres-dans-le-cadre-des-temps-forts-et-zooms-th%C3%A9matiques"
          isExternal
          icon={fullLinkIcon}
          opensInNewTab
          onClick={() =>
            logEvent(HighlightEvents.HAS_CLICKED_MORE_INFO_HIGHLIGHT)
          }
          label="En savoir plus sur les temps forts"
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
        />
        <Button
          as="a"
          to="https://passcultureapp.notion.site/1cfad4e0ff9880288df4c80eebfe3ca0?v=1cfad4e0ff9880f3bbfd000c6f5023f3"
          isExternal
          icon={fullLinkIcon}
          opensInNewTab
          onClick={() =>
            logEvent(HighlightEvents.HAS_CLICKED_CALENDAR_HIGHLIGHT)
          }
          label="Voir tout le calendrier"
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
        />
      </div>
      <DialogBuilder.Footer>
        <div className={styles['actions-container']}>
          <Dialog.Close asChild>
            <Button
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              label="Fermer"
            />
          </Dialog.Close>
          <Button
            as="a"
            to="/offres"
            variant={ButtonVariant.PRIMARY}
            onClick={() =>
              logEvent(HighlightEvents.HAS_CLICKED_ALL_OFFER_HIGHLIGHT)
            }
            label="Accéder à mes offres"
          />
        </div>
      </DialogBuilder.Footer>
    </DialogBuilder>
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
