import cn from 'classnames'
import { useState } from 'react'

import { Layout } from 'app/App/layout/Layout'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Header } from 'components/Header/Header'
import editFullIcon from 'icons/full-edit.svg'
import fullLeftIcon from 'icons/full-left.svg'
import fullRightIcon from 'icons/full-right.svg'
import connectStrokeIcon from 'icons/stroke-connect.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { RadioButtonWithImage } from 'ui-kit/RadioButtonWithImage/RadioButtonWithImage'

import styles from './OnboardingOfferIndividual.module.scss'

interface OnboardingOfferIndividualProps {
  className?: string
}

enum ONBOARDING_OFFER_TYPE {
  INDIVIDUAL = 'INDIVIDUAL',
  COLLECTIVE = 'COLLECTIVE',
}

export const OnboardingOfferIndividual = ({
  className,
}: OnboardingOfferIndividualProps): JSX.Element => {
  const [offerType, setOfferType] = useState<ONBOARDING_OFFER_TYPE | null>(null)

  const onChangeOfferType = (e: React.ChangeEvent<HTMLInputElement>) => {
    setOfferType(e.target.value as ONBOARDING_OFFER_TYPE)
  }

  return (
    <Layout layout="onboarding">
      <Header disableHomeLink={true} />
      <div className={cn(styles[`onboarding-offer-container`], className)}>
        <h1 className={styles['offers-title']}>
          Offre à destination des jeunes
        </h1>
        <FormLayout>
          <FormLayout.Section
            title="Comment souhaitez-vous créer votre 1ère offre ?"
            className={styles['offers-description']}
          >
            <FormLayout.Row
              inline
              mdSpaceAfter
              className={styles['individual-radio-button']}
            >
              <RadioButtonWithImage
                name="individualOfferSubtype"
                icon={editFullIcon}
                isChecked={offerType === ONBOARDING_OFFER_TYPE.INDIVIDUAL}
                label={`Créer une offre manuellement`}
                onChange={onChangeOfferType}
                value={ONBOARDING_OFFER_TYPE.INDIVIDUAL}
              />
            </FormLayout.Row>

            <FormLayout.Row
              inline
              mdSpaceAfter
              className={styles['individual-radio-button']}
            >
              <RadioButtonWithImage
                name="individualOfferSubtype"
                icon={connectStrokeIcon}
                isChecked={offerType === ONBOARDING_OFFER_TYPE.COLLECTIVE}
                label={`Créer automatiquement des offres via mon logiciel de gestion des stocks`}
                onChange={onChangeOfferType}
                value={ONBOARDING_OFFER_TYPE.COLLECTIVE}
              />
            </FormLayout.Row>
          </FormLayout.Section>
        </FormLayout>
      </div>

      <ActionsBarSticky hasSideNav={false}>
        <ActionsBarSticky.Left>
          <Button
            icon={fullLeftIcon}
            variant={ButtonVariant.SECONDARY}
            disabled={false}
          >
            Retour
          </Button>
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right>
          <Button
            type="submit"
            icon={fullRightIcon}
            iconPosition={IconPositionEnum.RIGHT}
            disabled={offerType === null}
          >
            Étape suivante
          </Button>
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OnboardingOfferIndividual
