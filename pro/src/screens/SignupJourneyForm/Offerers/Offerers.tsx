import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom-v5-compat'

import { useSignupJourneyContext } from 'context/SignupJourneyContext'
import { humanizeSiren } from 'core/Offerers/utils'
import useGetVenuesOfOffererFromSiretAdapter from 'core/Venue/adapters/getVenuesOfOffererFromSiretAdapter/useGetVenuesOfOffererFromSiretAdapter'
import { ArrowDownIcon, ArrowUpIcon } from 'icons'
import { Button, Title } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'

import { ActionBar } from '../ActionBar'

import styles from './Offerers.module.scss'

const Offerers = (): JSX.Element => {
  const navigate = useNavigate()
  const [isVenueListOpen, setIsVenueListOpen] = useState<boolean>(false)

  const { offerer } = useSignupJourneyContext()

  /* istanbul ignore next: redirect to offerer if there is no siret */
  const {
    isLoading: isLoadingVenues,
    error: venuesOfOffererError,
    data: venuesOfOfferer,
  } = useGetVenuesOfOffererFromSiretAdapter(offerer?.siret ?? '')

  const formatedSiret = humanizeSiren(venuesOfOfferer?.offererSiren)
  const displayToggleVenueList =
    venuesOfOfferer && venuesOfOfferer?.venues.length > 5

  useEffect(() => {
    if (venuesOfOffererError) {
      navigate('/parcours-inscription/structure')
    }
  }, [isLoadingVenues])

  if (isLoadingVenues) return <Spinner />

  return (
    <>
      <div className={styles['existing-offerers-layout']}>
        <Title level={1}>
          Nous avons trouvé un espace déjà inscrit sur le pass Culture et
          incluant ce SIRET.
        </Title>
        <Title level={4}>
          Rejoignez-le si votre structure se trouve dans la liste.
        </Title>
        <div className={styles['venues-layout']}>
          <Title level={4}>
            {venuesOfOfferer?.offererName} - {formatedSiret}
          </Title>
          <ul className={styles['venue-list']}>
            {venuesOfOfferer?.venues.map((venue, index) => (
              <li
                key={venue.id}
                hidden={
                  displayToggleVenueList && !isVenueListOpen && index >= 4
                }
              >
                {venue.name}
              </li>
            ))}
          </ul>
          {displayToggleVenueList && (
            <Button
              onClick={() => {
                setIsVenueListOpen(!isVenueListOpen)
              }}
              variant={ButtonVariant.TERNARY}
              Icon={isVenueListOpen ? ArrowUpIcon : ArrowDownIcon}
            >
              {isVenueListOpen
                ? 'Afficher moins de structures'
                : 'Afficher plus de structures'}
            </Button>
          )}
        </div>
        <Button variant={ButtonVariant.PRIMARY}>Rejoindre cet espace</Button>
      </div>
      <Title level={4} className={styles['wrong-offerer-title']}>
        Votre structure ne se trouve pas dans cette liste ?
      </Title>
      <Button
        onClick={() => navigate('/parcours-inscription/authentification')}
        variant={ButtonVariant.SECONDARY}
      >
        Ajouter une nouvelle structure
      </Button>
      <ActionBar
        previousStepTitle="Retour"
        hideRightButton
        onClickPrevious={() => navigate('/parcours-inscription/structure')}
        isDisabled={false}
      />
    </>
  )
}

export default Offerers
