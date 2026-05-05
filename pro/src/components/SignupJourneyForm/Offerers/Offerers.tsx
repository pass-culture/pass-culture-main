import cn from 'classnames'
import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { getHumanReadableApiError } from '@/apiClient/helpers'
import type { CreateOffererBodyModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { GET_VENUES_OF_OFFERER_FROM_SIRET_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  type Offerer,
  useSignupJourneyContext,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import {
  cleanSignupJourneyStorage,
  tryRestoreInitialAddressFromStorage,
  tryRestoreOffererFromStorage,
} from '@/commons/context/SignupJourneyContext/storage'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { initializeUser } from '@/commons/store/user/dispatchers/initializeUser'
import { ensureCurrentUser } from '@/commons/store/user/selectors'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { REGISTRATION_STEP_IDS } from '@/components/RegistrationStepper/constants'
import { generateVenueDataLines } from '@/components/SignupJourneyForm/Offerers/utils'
import { SIGNUP_JOURNEY_STEP_IDS } from '@/components/SignupJourneyStepper/constants'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullNextIcon from '@/icons/full-next.svg'
import { MAYBE_LOCAL_AUTHORITY_APE_CODE } from '@/pages/Signup/SignupContainer/constants'
import { SignupJourneyAction } from '@/pages/SignupJourneyRoutes/constants'
import { ConfirmDialog } from '@/ui-kit/ConfirmDialog/ConfirmDialog'
import { DescriptionList } from '@/ui-kit/DescriptionList/DescriptionList'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { ActionBar } from '../ActionBar/ActionBar'
import {
  DEFAULT_ADDRESS_FORM_VALUES,
  DEFAULT_OFFERER_FORM_VALUES,
} from '../Offerer/constants'
import styles from './Offerers.module.scss'

export const Offerers = (): JSX.Element => {
  const isSignupSimulationEnabled = useActiveFeature(
    'WIP_PRE_SIGNUP_SIMULATION'
  )

  const { logEvent } = useAnalytics()
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const currentUser = useAppSelector(ensureCurrentUser)

  const [showLinkDialog, setShowLinkDialog] = useState<boolean>(false)
  const [showAllVenues, setShowAllVenues] = useState<boolean>(false)

  const { offerer, initialAddress, setOfferer, setInitialAddress } =
    useSignupJourneyContext()
  const isLocalAuthority = MAYBE_LOCAL_AUTHORITY_APE_CODE.includes(
    offerer?.apeCode ?? ''
  )

  // TODO: this is causing a rerender of the component and a double call to `getVenuesOfOffererFromSiret`
  const joinSpaceButtonRef = useRef<HTMLButtonElement>(null)

  const {
    isLoading: isLoadingVenues,
    error: venuesOfOffererError,
    data: venuesOfOfferer,
  } = useSWR(
    offerer?.siret
      ? [GET_VENUES_OF_OFFERER_FROM_SIRET_QUERY_KEY, offerer.siret]
      : null,
    ([, offererSiret]) =>
      api.getVenuesOfOffererFromSiret(offererSiret.replaceAll(' ', '')),
    { isPaused: () => offerer?.siret === null }
  )

  const displayedVenuesNames = [
    venuesOfOfferer?.offererName ?? '',
    ...(venuesOfOfferer?.venues
      .filter((venue) => venue.siret === null)
      .map((venue) => venue.publicName) ?? []),
  ].sort((a, b) => a.localeCompare(b))

  const venuesLines = generateVenueDataLines(
    offerer,
    displayedVenuesNames,
    showAllVenues,
    setShowAllVenues
  )

  useEffect(() => {
    if (
      offerer === null ||
      offerer === DEFAULT_OFFERER_FORM_VALUES ||
      initialAddress === null ||
      initialAddress === DEFAULT_ADDRESS_FORM_VALUES
    ) {
      try {
        tryRestoreOffererFromStorage(setOfferer)
        tryRestoreInitialAddressFromStorage(setInitialAddress)
      } catch {
        cleanSignupJourneyStorage()
        navigate('/inscription/structure/recherche')
        return
      }
    }

    // In case of API error
    if (venuesOfOffererError) {
      navigate('/inscription/structure/recherche')
    }
  }, [
    offerer,
    setOfferer,
    initialAddress,
    setInitialAddress,
    venuesOfOffererError,
    navigate,
  ])

  if (isLoadingVenues || !offerer) {
    return <Spinner />
  }

  const redirectToOnboarding = () => {
    const newOfferer: Offerer = {
      ...offerer,
      createVenueWithoutSiret: true,
    }
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      to: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
      used: SignupJourneyAction.NewOfferer,
    })
    setOfferer(newOfferer)
    navigate('/inscription/structure/identification')
  }

  const doLinkAccount = async () => {
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      to: '/inscription/structure/rattachement/confirmation',
      used: SignupJourneyAction.JoinModal,
    })
    /* istanbul ignore next: venuesOfOfferer will always be defined here or else,
     the user would have been redirected */
    try {
      // TODO (igabriele, 202-10-20): Must be further DRYed via a proper decicaded dispatcher (see `Offerer.tsx`).
      const request: CreateOffererBodyModel = {
        city: offerer.city,
        name: venuesOfOfferer?.offererName ?? '',
        postalCode: offerer.postalCode,
        siren: offerer.siren ?? '',
      }
      const createdOfferer = await api.createOfferer(request)

      cleanSignupJourneyStorage()

      await dispatch(
        initializeUser({
          newOffererId: createdOfferer.id,
          user: {
            ...currentUser,
            hasUserOfferer: true,
          },
        })
      ).unwrap()

      navigate('/inscription/structure/rattachement/confirmation-rattachement')
    } catch (e) {
      snackBar.error(
        getHumanReadableApiError(
          e,
          'Impossible de lier votre compte à cette structure.'
        )
      )
    }
  }

  const doLinkUserToOfferer = () => {
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      to: 'LinkModal',
      used: SignupJourneyAction.LinkModalActionButton,
    })
    setShowLinkDialog(true)
  }

  const cancelLinkUserToOfferer = () => {
    logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
      from: 'LinkModal',
      to: location.pathname,
      used: SignupJourneyAction.LinkModalActionButton,
    })
    setShowLinkDialog(false)
  }

  return (
    <div
      className={cn({
        [styles['existing-offerers-container']]: isSignupSimulationEnabled,
      })}
    >
      <MainHeading
        className={styles['main-heading']}
        mainHeading="Ce SIRET est déjà inscrit"
      />
      <p className={styles['subheading-description']}>
        Ce SIRET est déjà associé à{' '}
        {pluralizeFr(
          displayedVenuesNames.length,
          'une structure',
          'plusieurs structures'
        )}{' '}
        sur le pass Culture Pro.
      </p>

      <div className={styles['venues-layout']}>
        <DescriptionList lines={venuesLines} />
      </div>

      <div className={styles['next-actions']}>
        {isSignupSimulationEnabled && (
          <Button
            as="a"
            variant={ButtonVariant.SECONDARY}
            onClick={() => {
              setOfferer(null)
              logEvent(Events.CLICKED_ONBOARDING_FORM_NAVIGATION, {
                from: location.pathname,
                to: REGISTRATION_STEP_IDS.SIRET,
                used: SignupJourneyAction.ActionBar,
              })
            }}
            to="/inscription/structure/recherche"
            label="Retour"
          />
        )}

        <Button
          onClick={doLinkUserToOfferer}
          ref={joinSpaceButtonRef}
          label="Rejoindre cet espace"
        />
      </div>

      {isLocalAuthority && (
        <>
          <div className={styles['wrong-offerer-title']}>
            Vous souhaitez ajouter une nouvelle structure à cet espace ?
          </div>
          <Button
            onClick={redirectToOnboarding}
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            label="Ajouter une nouvelle structure"
            iconPosition={IconPositionEnum.LEFT}
            icon={fullNextIcon}
          />
        </>
      )}

      {!isSignupSimulationEnabled && (
        <ActionBar
          previousStepTitle="Retour à la recherche de SIRET"
          hideRightButton
          onClickPrevious={() => {
            setOfferer(null)
            navigate('/inscription/structure/recherche')
          }}
          previousTo={SIGNUP_JOURNEY_STEP_IDS.OFFERER}
          isDisabled={false}
        />
      )}

      <ConfirmDialog
        hideIcon={true}
        onCancel={cancelLinkUserToOfferer}
        title="Rejoindre cet espace ?"
        onConfirm={doLinkAccount}
        confirmText="Rejoindre cet espace"
        cancelText="Annuler"
        extraClassNames={styles['dialog-content']}
        open={showLinkDialog}
        refToFocusOnClose={joinSpaceButtonRef}
      >
        <div className={styles['dialog-info']}>
          Votre demande sera transmise à nos équipes, qui valideront votre
          rattachement par email.
        </div>
      </ConfirmDialog>
    </div>
  )
}
