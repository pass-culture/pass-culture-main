import * as Dialog from '@radix-ui/react-dialog'
import type { ReactNode } from 'react'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_HIGHLIGHTS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { HighlightEvents } from '@/commons/core/FirebaseEvents/constants'
import { formatDate } from '@/commons/utils/date'
import { Tag } from '@/design-system/Tag/Tag'
import fullLinkIcon from '@/icons/full-link.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'
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
        <Callout
          title="Comment participer ?"
          variant={CalloutVariant.INFO}
          className={styles['callout']}
        >
          <ul>
            <li>
              - Créez votre offre d’évènement ou choisissez en une dans votre
              liste d’offres
            </li>
            <li>- Ouvrez votre offre</li>
            <li>- Choisissez le temps fort</li>
          </ul>
        </Callout>
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
                  availabilityTimespan,
                  highlightTimespan,
                }) => (
                  // biome-ignore lint/a11y/useSemanticElements: correct voiceover bug with list displayed with flex
                  // biome-ignore lint/a11y/noRedundantRoles: idem
                  <li key={id} role="listitem">
                    <HighlightCard
                      imageSrc={mediationUrl}
                      title={name}
                      availabilityTimespan={availabilityTimespan}
                      highlightTimespan={highlightTimespan}
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
        <ButtonLink
          to="https://aide.passculture.app/hc/fr/articles/20587966046748--Acteurs-Culturels-Comment-et-pourquoi-proposer-des-offres-dans-le-cadre-des-temps-forts-et-zooms-th%C3%A9matiques"
          isExternal
          icon={fullLinkIcon}
          opensInNewTab
          onClick={() =>
            logEvent(HighlightEvents.HAS_CLICKED_MORE_INFO_HIGHLIGHT)
          }
        >
          En savoir plus sur les temps forts
        </ButtonLink>
        <ButtonLink
          to="https://passcultureapp.notion.site/1cfad4e0ff9880288df4c80eebfe3ca0?v=1cfad4e0ff9880f3bbfd000c6f5023f3"
          isExternal
          icon={fullLinkIcon}
          opensInNewTab
          onClick={() =>
            logEvent(HighlightEvents.HAS_CLICKED_CALENDAR_HIGHLIGHT)
          }
        >
          Voir tout le calendrier
        </ButtonLink>
      </div>
      <DialogBuilder.Footer>
        <div className={styles['actions-container']}>
          <Dialog.Close asChild>
            <Button variant={ButtonVariant.SECONDARY}>Fermer</Button>
          </Dialog.Close>
          <ButtonLink
            to="/offres"
            variant={ButtonVariant.PRIMARY}
            onClick={() =>
              logEvent(HighlightEvents.HAS_CLICKED_ALL_OFFER_HIGHLIGHT)
            }
          >
            Accéder à mes offres
          </ButtonLink>
        </div>
      </DialogBuilder.Footer>
    </DialogBuilder>
  )
}

type HighlightCardProps = {
  imageSrc: string
  title: ReactNode
  children: ReactNode
  availabilityTimespan: string[]
  highlightTimespan: string[]
}

const HighlightCard = ({
  imageSrc,
  title,
  children,
  availabilityTimespan,
  highlightTimespan,
}: HighlightCardProps) => {
  return (
    <div className={styles['card']}>
      <div className={styles['card-content']}>
        <img src={imageSrc} alt="" className={styles['card-image']} />
        <Tag
          label={`Du ${formatDate(highlightTimespan[0])} au ${formatDate(highlightTimespan[1])}`}
        />
        <h3 className={styles['card-title']}>{title}</h3>
        <p className={styles['card-description']}>{children}</p>
        <p className={styles['card-limit-participation-date']}>
          Date limite de participation : {formatDate(availabilityTimespan[1])}
        </p>
      </div>
    </div>
  )
}
