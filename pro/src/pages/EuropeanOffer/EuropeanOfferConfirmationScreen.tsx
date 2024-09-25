import { useTranslation } from 'react-i18next'

import fullValidateIcon from 'icons/full-validate.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './IndividualOfferConfirmationScreen.module.scss'

export const EuropeanOfferConfirmationScreen = (): JSX.Element => {
  const { t } = useTranslation('common')

  return (
    <div className={styles['confirmation-container']}>
      <div>
        <SvgIcon
          src={fullValidateIcon}
          alt=""
          className={styles['validate-icon']}
        />
        <h2 className={styles['confirmation-title']}>Offre publiée !</h2>
        <p className={styles['confirmation-details']}>
          {t('confirmation_description')}
        </p>
      </div>
      <div className={styles['confirmation-actions']}>
        <ButtonLink
          to={'/offre/creation'}
          isExternal
          className={styles['confirmation-action']}
          variant={ButtonVariant.SECONDARY}
        >
          {t('create_a_new_offer')}
        </ButtonLink>
      </div>
    </div>
  )
}
