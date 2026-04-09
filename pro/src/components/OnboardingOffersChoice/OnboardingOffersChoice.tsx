import { addDays } from 'date-fns'
import { useState } from 'react'
import { useNavigate } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { OnboardingDidacticEvents } from '@/commons/core/FirebaseEvents/constants'
import { NBSP } from '@/commons/core/shared/constants'
import { COOKIES } from '@/commons/utils/localStorageManager'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullNextIcon from '@/icons/full-next.svg'
import { Card } from '@/ui-kit/Card/Card'
import { Dialog } from '@/ui-kit/Dialog/Dialog'

import collective from './assets/collective.jpeg'
import individuelle from './assets/individuelle.jpeg'
import { OnboardingCollectiveModal } from './components/OnboardingCollectiveModal/OnboardingCollectiveModal'
import styles from './OnboardingOffersChoice.module.scss'

export const OnboardingOffersChoice = () => {
  const [showModal, setShowModal] = useState(false)
  const { logEvent } = useAnalytics()
  const navigate = useNavigate()

  return (
    <>
      <div className={styles['card-container']}>
        <Card>
          <Card.Image src={individuelle} alt="" />
          <Card.Header
            title="Sur l’application mobile à destination des jeunes"
            titleTag="h3"
          />
          <Card.Content>
            <span>
              Vos offres seront visibles par{' '}
              <strong className={styles['card-description-highlight']}>
                + de 4 millions de jeunes
              </strong>
              {NBSP}
              inscrits sur l’application mobile pass Culture.
            </span>
          </Card.Content>
          <Card.Footer>
            <Button
              as="a"
              variant={ButtonVariant.PRIMARY}
              to="/onboarding/individuel"
              aria-label="Commencer la création d’offre sur l’application mobile"
              fullWidth
              label="Commencer"
            />
          </Card.Footer>
        </Card>

        <Card>
          <Card.Image src={collective} alt="" />
          <Card.Header title="Sur ADAGE à destination des enseignants" />
          <Card.Content>
            <span>
              Vos offres seront visibles{' '}
              <strong className={styles['card-description-highlight']}>
                par tous les enseignants
              </strong>{' '}
              des collèges et lycées publics et privés sous contrat.
            </span>
          </Card.Content>
          <Card.Footer>
            <Dialog
              title=""
              onCancel={() => setShowModal(false)}
              hideIcon={true}
              trigger={
                <Button
                  type="submit"
                  aria-label="Commencer la création d’offre sur ADAGE"
                  onClick={() => {
                    logEvent(
                      OnboardingDidacticEvents.HAS_CLICKED_START_COLLECTIVE_DIDACTIC_ONBOARDING
                    )
                    setShowModal(true)
                  }}
                  fullWidth
                  label="Commencer"
                />
              }
              open={showModal}
            >
              <OnboardingCollectiveModal />
            </Dialog>
          </Card.Footer>
        </Card>
      </div>
      <div className={styles['skip-link-wrapper']}>
        <Button
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          icon={fullNextIcon}
          iconPosition={IconPositionEnum.RIGHT}
          label="Je le ferai plus tard"
          onClick={() => {
            const tomorrow = addDays(new Date(), 1)
            // biome-ignore lint/suspicious/noDocumentCookie: Cookie Store API is only available on firefox as of 2025-06-24
            document.cookie = `${COOKIES.DID_SKIP_ONBOARDING}=true; expires=${tomorrow.toUTCString()}; path=/;`

            setTimeout(() => {
              navigate('/accueil')
            })
          }}
        />
      </div>
    </>
  )
}
