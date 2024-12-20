import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { FormLayout } from 'components/FormLayout/FormLayout'
import editFullIcon from 'icons/full-edit.svg'
import connectStrokeIcon from 'icons/stroke-connect.svg'
import { RadioButtonWithImage } from 'ui-kit/RadioButtonWithImage/RadioButtonWithImage'

import { ActionBar } from '../components/ActionBar/ActionBar'
import { OnboardingLayout } from '../components/OnboardingLayout/OnboardingLayout'

import styles from './OnboardingOfferIndividual.module.scss'

type OnboardingOfferProcedure = 'MANUAL' | 'AUTOMATIC'

// Mapping the redirect URLs to the corresponding offer type
const urls: Record<OnboardingOfferProcedure, string> = {
  MANUAL: '/onboarding/offre/creation',
  AUTOMATIC: '/onboarding/synchro',
} as const

export const OnboardingOfferIndividual = (): JSX.Element => {
  const [offerType, setOfferType] = useState<OnboardingOfferProcedure>('MANUAL')
  const navigate = useNavigate()

  const onChangeOfferType = (e: React.ChangeEvent<HTMLInputElement>) => {
    setOfferType(e.target.value as OnboardingOfferProcedure)
  }

  return (
    <OnboardingLayout verticallyCentered showFooter={false}>
      <h1 className={styles['offers-title']}>Offre à destination des jeunes</h1>
      <h2 className={styles['offers-subtitle']}>
        Comment souhaitez-vous créer votre 1ère offre ?
      </h2>

      <FormLayout>
        <FormLayout.Section className={styles['offers-description']}>
          <FormLayout.Row
            inline
            mdSpaceAfter
            className={styles['individual-radio-button']}
          >
            <RadioButtonWithImage
              name="individualOfferSubtype"
              icon={editFullIcon}
              isChecked={offerType === 'MANUAL'}
              label={`Créer une offre manuellement`}
              onChange={onChangeOfferType}
              value={'MANUAL'}
              className={styles['individual-radio-label']}
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
              isChecked={offerType === 'AUTOMATIC'}
              label={`Créer automatiquement des offres via mon logiciel de gestion des stocks`}
              onChange={onChangeOfferType}
              value={'AUTOMATIC'}
              className={styles['individual-radio-label']}
            />
          </FormLayout.Row>
        </FormLayout.Section>
      </FormLayout>

      <ActionBar
        withNextButton
        onLeftButtonClick={() => navigate('/onboarding')}
        onRightButtonClick={() => navigate(urls[offerType])}
      />
    </OnboardingLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OnboardingOfferIndividual
