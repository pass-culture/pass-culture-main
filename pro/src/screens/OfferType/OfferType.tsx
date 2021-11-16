import cn from 'classnames'
import React, { useState } from 'react'
import { Link } from 'react-router-dom'

import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'
import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as UserIcon } from 'icons/user.svg'
import { SubmitButton } from 'ui-kit'

import { OFFER_TYPES } from './constants'
import styles from './OfferType.module.scss'
import OfferTypeButton from './OfferTypeButton'

const { INDIVIDUAL_OR_DUO, EDUCATIONAL } = OFFER_TYPES

interface IOfferTypeProps {
  fetchCanOffererCreateEducationalOffer: () => void;
}

const OfferType = ({
  fetchCanOffererCreateEducationalOffer
}: IOfferTypeProps): JSX.Element => {
  const [offerType, setOfferType] = useState(INDIVIDUAL_OR_DUO)

  const getNextPageHref = () => {
    if (offerType === INDIVIDUAL_OR_DUO) {
      return '/offres/creation'
    }

    return '/offres/eac/creation'
  }

  return (
    <div>
      <h1
        className={styles['offer-type-title']}
      >
        Créer une nouvelle offre
      </h1>
      <h2 className={styles['offer-type-description']}>
        Quel type d’offre souhaitez-vous proposer ?
      </h2>
      <div className={styles['offer-type-buttons']}>
        <OfferTypeButton
          Icon={UserIcon}
          className={styles['offer-type-buttons-button']}
          isSelected={offerType === INDIVIDUAL_OR_DUO}
          label='Une offre à destination du grand public'
          onClick={() => setOfferType(INDIVIDUAL_OR_DUO)}
        />
        <OfferTypeButton
          Icon={LibraryIcon}
          className={styles['offer-type-buttons-button']}
          isSelected={offerType === EDUCATIONAL}
          label="Une offre à destination d'un groupe scolaire"
          onClick={() => setOfferType(EDUCATIONAL)}
        />
      </div>
      <div className={styles['offer-type-actions']}>
        <Link
          className={cn(styles['offer-type-actions-action'], "secondary-link")}
          to={computeOffersUrl({})}
        >
          Retour
        </Link>
        <SubmitButton
          className={cn(styles['offer-type-actions-action'], "primary-button")}
          disabled={false}
          isLoading={false}
          onClick={getNextPageHref}
        >
          Étape suivante
        </SubmitButton>
      </div>
    </div>
  )
}

export default OfferType
