import cn from 'classnames'
import { useState } from 'react'
import { useNavigate } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { WelcomeCarouselEvents } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/design-system/Button/Button'
import { Icon } from '@/design-system/Button/components/Icon/Icon'
import { ButtonVariant } from '@/design-system/Button/types'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import strokeBagIcon from '@/icons/stroke-bag.svg'
import strokeBookIcon from '@/icons/stroke-book.svg'
import strokeComedyIcon from '@/icons/stroke-comedy.svg'
import strokeLocationIcon from '@/icons/stroke-location.svg'

import commonStyles from '../CommonWelcomeCarousel.module.scss'
import styles from './WelcomeStepHub.module.scss'

export const WelcomeStepHub = (): JSX.Element => {
  const navigate = useNavigate()
  const { logEvent } = useAnalytics()

  const [selectedValue, setSelectedValue] = useState('')
  const [showErrorContainer, setShowErrorContainer] = useState(false)
  return (
    <>
      {showErrorContainer && (
        <>
          <div
            className={cn(commonStyles[`container`], styles['icon-container'])}
          >
            <Icon iconClassName={styles.icon} icon={strokeLocationIcon} />
            <h1 className={commonStyles.title}>
              Mince, vous êtes au mauvais endroit !
            </h1>
            <h2 className={commonStyles.subtitle}>
              Pour réserver des activités culturelles avec vos classes, utilisez
              la plateforme ADAGE.
            </h2>
          </div>
          <div
            className={cn(
              commonStyles[`actionbar-container`],
              commonStyles[`actionbar-container-single`]
            )}
          >
            <Button
              onClick={() => {
                setSelectedValue('')
                setShowErrorContainer(false)
              }}
              variant={ButtonVariant.SECONDARY}
              label="Retour"
            />
            <Button
              as="a"
              to="https://adage-pr.phm.education.gouv.fr/ds/?entityID=https%3A%2F%2Fadage-pr.phm.education.gouv.fr%2Fsp%2Fmdp&return=https%3A%2F%2Fadage-pr.phm.education.gouv.fr%2Fmdp%2FShibboleth.sso%2FLogin%3FSAMLDS%3D1%26target%3Dss%253Amem%253Af7ae5c254ceec3841749f8747ba4ff685aa80d7e05b232b3d8902796e9d36bab%26authnContextClassRef%3Durn%253Aoasis%253Anames%253Atc%253ASAML%253A2.0%253Aac%253Aclasses%253APasswordProtectedTransport%2520urn%253Aoasis%253Anames%253Atc%253ASAML%253A2.0%253Aac%253Aclasses%253ATimeSyncToken"
              isExternal={true}
              variant={ButtonVariant.PRIMARY}
              label="Accéder à ADAGE"
              onClick={() =>
                logEvent(WelcomeCarouselEvents.HAS_CLICKED_ADAGE_LINK)
              }
            />
          </div>
        </>
      )}
      {!showErrorContainer && (
        <>
          <h1 className={commonStyles.title}>Bienvenue sur pass Culture Pro</h1>
          <h2 className={commonStyles.subtitle}>
            Commençons par identifier votre profil
          </h2>
          <div className={commonStyles[`container`]}>
            <RadioButtonGroup
              name="group"
              label="Vous êtes :"
              checkedOption={selectedValue}
              options={[
                {
                  label: 'Partenaire culturel',
                  description:
                    'Je travaille dans le secteur culturel et je souhaite proposer des offres',
                  asset: {
                    variant: 'icon',
                    src: strokeComedyIcon,
                  },
                  value: 'partenaire-culturel',
                  checked: selectedValue === 'partenaire-culturel',
                },
                {
                  label: 'Jeune',
                  description:
                    'J’ai entre 15 et 21 ans et je veux réserver des offres',
                  asset: {
                    variant: 'icon',
                    src: strokeBagIcon,
                  },
                  value: 'jeune',
                  checked: selectedValue === 'jeune',
                },
                {
                  label: 'Personnel enseignant',
                  description:
                    'Je souhaite réserver des activités culturelles pour mes élèves',
                  asset: {
                    variant: 'icon',
                    src: strokeBookIcon,
                  },
                  value: 'enseignant',
                  checked: selectedValue === 'enseignant',
                },
              ]}
              variant="detailed"
              display="vertical"
              onChange={(event) => {
                setSelectedValue(event.target.value)
              }}
            />
          </div>
          <div
            className={cn(
              commonStyles[`actionbar-container`],
              commonStyles[`actionbar-container-single`]
            )}
          >
            <Button
              disabled={!selectedValue}
              onClick={() => {
                logEvent(WelcomeCarouselEvents.HAS_CLICKED_USER_TYPE, {
                  target: selectedValue,
                })
                switch (selectedValue) {
                  case 'partenaire-culturel':
                    navigate('/bienvenue/publics')
                    break
                  case 'jeune':
                    globalThis.location.href =
                      'https://passculture.app/creation-compte'
                    break
                  case 'enseignant':
                    setShowErrorContainer(true)
                    break
                }
              }}
              variant={ButtonVariant.PRIMARY}
              label="Continuer"
            />
          </div>
        </>
      )}
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = WelcomeStepHub
