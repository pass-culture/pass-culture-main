import { useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { EngagementEvents } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { Card } from '@/ui-kit/Card/Card'

import { ModalHighlight } from '../HighlightHome/ModalHighlight/ModalHighlight'
import cultureSurvey from './assets/culture-survey.png'
import headlineOffer from './assets/headline-offer.png'
import highlightOffer from './assets/highlight-offer.png'
import offerRecommendation from './assets/offer-recommendation.png'
import { EditoCardItem } from './components/EditoCardItem'
import styles from './EditoCard.module.scss'

export const EditoCard = ({
  canDisplayHighlights,
  venueId,
}: {
  canDisplayHighlights: boolean
  venueId: number
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const { logEvent } = useAnalytics()

  const highlightOfferCard = (
    <EditoCardItem
      image={highlightOffer}
      title="Valoriser vos évènements sur le pass Culture !"
      subtitle="Valorisez vos évènements en les associant à un temps fort du pass Culture ! Un temps fort permet de valoriser vos offres autour d'une thématique."
      footer={
        <ModalHighlight
          open={isModalOpen}
          onOpenChange={setIsModalOpen}
          trigger={
            <Button
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              size={ButtonSize.SMALL}
              fullWidth={true}
              onClick={() =>
                logEvent(EngagementEvents.HAS_REQUESTED_HIGHLIGHTS, {
                  venueId,
                  action: 'discover',
                })
              }
              label="Parcourir les temps forts"
            />
          }
        />
      }
    />
  )

  const culturalSurveyCard = (
    <EditoCardItem
      image={cultureSurvey}
      title="[Enquête pass Culture] les 15-20 ans et leur rapport à la culture"
      subtitle="Découvrez les résultats de l'enquête pass Culture sur les jeunes et leurs rapport à la culture !"
      footer={
        <Button
          label="Lire l’enquête"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
          isExternal={true}
          opensInNewTab={true}
          fullWidth={true}
          as="a"
          to="https://pass.culture.fr/ressources/references-culturelles-best-of-2025"
        />
      }
    />
  )

  const headlineOfferCard = (
    <EditoCardItem
      image={headlineOffer}
      title="Mettez une offre en valeur sur votre page de l'application"
      subtitle="Votre offre à la une sera mise en avant sur votre page sur l'application."
      footer={
        <Button
          label="Choisir une offre"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
          fullWidth={true}
          to="/offres"
          as="a"
        />
      }
    />
  )

  const recommendationCard = (
    <EditoCardItem
      image={offerRecommendation}
      title="Écrivez une recommandation pour conseiller votre offre"
      subtitle="Partagez votre expertise en conseillant une ou plusieurs offres aux jeunes."
      footer={
        <Button
          label="Choisir une offre"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
          fullWidth={true}
          to="/offres"
          as="a"
        />
      }
    />
  )

  return (
    <Card>
      <Card.Header title="Comment valoriser vos offres auprès du public jeune ?" />
      <Card.Content>
        <div className={styles['content']}>
          {canDisplayHighlights ? (
            <>
              {highlightOfferCard}
              {headlineOfferCard}
            </>
          ) : (
            <>
              {headlineOfferCard}
              {recommendationCard}
            </>
          )}
          {culturalSurveyCard}
        </div>
      </Card.Content>
    </Card>
  )
}
