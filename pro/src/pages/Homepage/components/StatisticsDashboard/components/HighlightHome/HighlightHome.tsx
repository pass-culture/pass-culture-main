import * as Dialog from '@radix-ui/react-dialog'
import { type ReactNode, useState } from 'react'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_HIGHLIGHTS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'
import { Card } from '@/ui-kit/Card/Card'
import {
  DialogBuilder,
  type DialogBuilderProps,
} from '@/ui-kit/DialogBuilder/DialogBuilder'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import highlightImg from './assets/highlight.png'
import styles from './Highlight.module.scss'

export const HighlightHome = () => {
  const [isOpen, setIsOpen] = useState(false)
  return (
    <Card
      imageSrc={highlightImg}
      title={
        <h3>
          Valorisez vos évènements en les associant à un temps fort du pass
          Culture !
        </h3>
      }
      actions={
        <ModalHighlight
          onOpenChange={setIsOpen}
          open={isOpen}
          trigger={
            <Button variant={ButtonVariant.SECONDARY}>
              Parcourir les temps forts
            </Button>
          }
        />
      }
    >
      Un temps fort permet de valoriser vos offres événements autour d’une
      thématique.
    </Card>
  )
}

interface ModalHighlight extends Omit<DialogBuilderProps, 'children'> {}

export const ModalHighlight = ({
  ...dialogBuilderProps
}: ModalHighlight): JSX.Element | null => {
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
        <Callout variant={CalloutVariant.INFO}>
          <ul>
            <li>
              Créez votre offre d’évènement ou choisissez en une dans votre
              liste d’offre
            </li>
            <li>Ouvrez votre offre</li>
            <li>Choisissez le temps fort</li>
          </ul>
        </Callout>
        {isLoading ? (
          <Spinner />
        ) : (
          data?.map(({ id, description, mediationUrl, name }) => (
            <HighlightCard key={id} imageSrc={mediationUrl} title={name}>
              {description}
            </HighlightCard>
          ))
        )}
      </div>
      <DialogBuilder.Footer>
        <div>
          <Dialog.Close asChild>
            <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
          </Dialog.Close>
          <Button>Ajouter</Button>
        </div>
      </DialogBuilder.Footer>
    </DialogBuilder>
  )
}

type HighlightCardProps = {
  imageSrc: string
  title: ReactNode
  children: ReactNode
}

const HighlightCard = ({ imageSrc, title, children }: HighlightCardProps) => {
  return (
    <div className={styles['card']}>
      <div className={styles['card-content']}>
        <div>
          <img src={imageSrc} alt="" className={styles['card-image']} />
          {title}
          <p className={styles['card-description']}>{children}</p>
        </div>
      </div>
    </div>
  )
}
