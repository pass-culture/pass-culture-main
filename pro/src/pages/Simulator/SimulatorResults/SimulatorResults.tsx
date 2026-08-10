import { Banner, BannerVariants } from 'design-system/Banner/Banner'
import { useSimulatorContext } from 'pages/Simulator/SimulatorContext'
import {
  getAlertContent,
  getDocumentCardContent,
} from 'pages/Simulator/SimulatorResults/utils'
import {
  tryRestoreActivityFromStorage,
  tryRestoreOpenToPublicFromStorage,
  tryRestoreSiretFromStorage,
  tryRestoreTargetAudienceFromStorage,
} from 'pages/Simulator/storage'
import { useEffect, useState } from 'react'
import { InfoPanel } from 'ui-kit/InfoPanel/InfoPanel'
import { InfoPanelSize, InfoPanelSurface } from 'ui-kit/InfoPanel/types'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { sendSentryCustomError } from '@/commons/utils/sendSentryCustomError'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import nextIcon from '@/icons/full-next.svg'
import commonStyles from '@/pages/Simulator/CommonSimulator.module.scss'

import { api } from 'apiClient/api'
import {
  type ActivityNotOpenToPublic,
  type ActivityOpenToPublic,
  SignupSimulationMessageLevel,
  type SignupSimulationMessageModel,
  type SignupSimulationResponseModel,
  TargetAudience,
} from 'apiClient/v1'
import styles from './SimulatorResults.module.scss'

function targetAudiencesToTargets(
  targetAudiences:
    | Partial<Record<'individual' | 'collective', boolean | undefined>>
    | undefined
): TargetAudience[] {
  const targets = []
  if (targetAudiences?.individual) {
    targets.push(TargetAudience.INDIVIDUAL)
  }
  if (targetAudiences?.collective) {
    targets.push(TargetAudience.COLLECTIVE)
  }
  return targets
}

export const SimulatorResults = (): JSX.Element => {
  const {
    openToPublic,
    setOpenToPublic,
    activity,
    setActivity,
    siret,
    setSiret,
    targetAudiences,
    setTargetAudiences,
  } = useSimulatorContext()

  const [result, setResult] = useState<
    SignupSimulationResponseModel | undefined
  >()
  const [showErrorBanner, setShowErrorBanner] = useState<boolean>(false)

  useEffect(() => {
    const doCall = async () => {
      try {
        setShowErrorBanner(false)
        const finalOpenToPublic =
          openToPublic ?? tryRestoreOpenToPublicFromStorage(setOpenToPublic)
        const finalActivity =
          (activity as ActivityOpenToPublic | ActivityNotOpenToPublic) ||
          tryRestoreActivityFromStorage(setActivity)
        const finalSiret = siret ?? tryRestoreSiretFromStorage(setSiret)
        const finalTargetAudience =
          targetAudiences?.individual !== undefined
            ? targetAudiences
            : tryRestoreTargetAudienceFromStorage(setTargetAudiences)

        const targets = targetAudiencesToTargets(finalTargetAudience)

        if (
          !finalActivity ||
          !finalOpenToPublic ||
          !finalSiret ||
          targets.length === 0
        ) {
          return
        }

        const simulationResponse = await api.simulateSignup({
          body: {
            activity: finalActivity,
            isOpenToPublic: finalOpenToPublic === 'true',
            siret: finalSiret.replaceAll(' ', '') ?? '',
            targets,
          },
        })
        setResult(simulationResponse)
      } catch (e) {
        sendSentryCustomError(e)
        setShowErrorBanner(true)
      }
    }
    doCall()
  }, [
    activity,
    openToPublic,
    setActivity,
    setOpenToPublic,
    setSiret,
    setTargetAudiences,
    siret,
    targetAudiences,
  ])

  const buildSignupLink = (): string => {
    const searchParams = new URLSearchParams(
      Object.entries({
        ...(openToPublic && { isOpenToPublic: openToPublic }),
        ...(activity && { activity }),
        ...(siret && { siret }),
      })
    )
    if (targetAudiences) {
      targetAudiencesToTargets(targetAudiences).forEach(
        (item: TargetAudience) => {
          searchParams.append('targets', String(item))
        }
      )
    }

    const queryString = searchParams.toString()

    return queryString
      ? `/inscription/compte/creation?${queryString}`
      : '/inscription/compte/creation'
  }

  if (!result && !showErrorBanner) {
    return <Spinner />
  }

  return (
    <>
      <div className={commonStyles['content']}>
        <h1 className={commonStyles['title']}>
          Voici les justificatifs à préparer pour votre inscription
        </h1>
      </div>
      {showErrorBanner && (
        <Banner
          title="Impossible d'afficher vos documents justificatifs"
          description="Une erreur est survenue de notre côté. Vous pourrez renseigner ces informations directement dans la suite de votre inscription."
          variant={BannerVariants.ERROR}
        />
      )}
      <div className={styles['documents']}>
        {result?.eligibilityDocuments.map((document, index: number) => {
          const { title, description } = getDocumentCardContent(document)
          return (
            <InfoPanel
              surface={InfoPanelSurface.ELEVATED}
              size={InfoPanelSize.SMALL}
              title={title}
              stepNumber={index + 1}
              key={title}
              titleLevel="2"
            >
              {description}
            </InfoPanel>
          )
        })}
        {result?.messages.map((message: SignupSimulationMessageModel) => {
          const content = getAlertContent(message.type)
          return (
            <Banner
              title={content.title}
              key={message.type}
              variant={
                message.level === SignupSimulationMessageLevel.ALERT
                  ? BannerVariants.WARNING
                  : BannerVariants.DEFAULT
              }
              actions={content.link}
              closable={false}
              description={content.description}
            />
          )
        })}
      </div>
      <div className={commonStyles['action-bar']}>
        <Button
          as="router-link"
          to={
            showErrorBanner
              ? '/inscription/preparation/siret'
              : '/inscription/preparation/publics'
          }
          variant={ButtonVariant.SECONDARY}
          label={showErrorBanner ? 'Recommencer' : 'Retour'}
        />
        <Button as="router-link" to={buildSignupLink()} label="Continuer" />
      </div>

      {!showErrorBanner && (
        <aside className={styles['signup-later']}>
          <p className={styles['signup-later-text']}>
            Vous souhaitez vous inscrire plus tard ?
          </p>
          <Button
            as="a"
            to="/inscription/preparation/email"
            icon={nextIcon}
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            label="Recevoir la liste par email"
          />
        </aside>
      )}
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorResults
