import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { FormLayout } from 'components/FormLayout/FormLayout'
import editFullIcon from 'icons/full-edit.svg'
import connectStrokeIcon from 'icons/stroke-connect.svg'
import { RadioButtonWithImage } from 'ui-kit/RadioButtonWithImage/RadioButtonWithImage'

import { ActionBar } from '../components/ActionBar/ActionBar'
import { OnboardingLayout } from '../components/OnboardingLayout/OnboardingLayout'

import styles from './OnboardingOfferIndividual.module.scss'

const ONBOARDING_OFFER_PROCEDURE = {
  MANUAL: 'MANUAL',
  AUTOMATIC: 'AUTOMATIC',
} as const
// eslint-disable-next-line no-redeclare, @typescript-eslint/naming-convention
type ONBOARDING_OFFER_PROCEDURE =
  (typeof ONBOARDING_OFFER_PROCEDURE)[keyof typeof ONBOARDING_OFFER_PROCEDURE]

// Mapping the redirect URLs to the corresponding offer type
const urls: Record<ONBOARDING_OFFER_PROCEDURE, string> = {
  MANUAL: '/inscription-offre-individuelle-manuelle',
  AUTOMATIC: '/inscription-offre-individuelle-auto',
} as const

export const OnboardingOfferIndividual = (): JSX.Element => {
  const [offerType, setOfferType] = useState<ONBOARDING_OFFER_PROCEDURE | null>(
    null
  )
  const navigate = useNavigate()

  const onChangeOfferType = (e: React.ChangeEvent<HTMLInputElement>) => {
    setOfferType(e.target.value as ONBOARDING_OFFER_PROCEDURE)
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
              isChecked={offerType === ONBOARDING_OFFER_PROCEDURE.MANUAL}
              label={`Créer une offre manuellement`}
              onChange={onChangeOfferType}
              value={ONBOARDING_OFFER_PROCEDURE.MANUAL}
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
              isChecked={offerType === ONBOARDING_OFFER_PROCEDURE.AUTOMATIC}
              label={`Créer automatiquement des offres via mon logiciel de gestion des stocks`}
              onChange={onChangeOfferType}
              value={ONBOARDING_OFFER_PROCEDURE.AUTOMATIC}
              className={styles['individual-radio-label']}
            />
          </FormLayout.Row>
        </FormLayout.Section>
      </FormLayout>

      <ActionBar
        disableRightButton={offerType === null}
        withNextButton
        onLeftButtonClick={() => navigate(-1)}
        onRightButtonClick={() => {
          if (offerType) {
            navigate(urls[offerType])
          }
        }}
      />
    </OnboardingLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OnboardingOfferIndividual
