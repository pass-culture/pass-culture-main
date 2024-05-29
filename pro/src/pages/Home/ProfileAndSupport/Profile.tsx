import React from 'react'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import { useCurrentUser } from 'hooks/useCurrentUser'
import fullEditIcon from 'icons/full-edit.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import { Card } from '../Card'

import styles from './Profile.module.scss'

/**
 * if phone number is valid:
 * - 10 digit starting by 0
 * - n digits starting by +
 *
 * return formated phone number:
 * - 01 23 45 67 89
 * - +213 1 23 45 67 89
 *
 * otherwise, return given argument phoneNumber unchanged
 */
export const formatPhoneNumber = (phoneNumber: string | null | undefined) => {
  let formatedNumber = phoneNumber
  if (phoneNumber) {
    formatedNumber = phoneNumber.replace(/ /g, '')
    const r = /(\+?[0-9]+)([0-9])([0-9]{8})/g
    const parts = formatedNumber.split(r).slice(1, -1)

    if (parts.length !== 3) {
      return phoneNumber
    }

    const [internationalPrefix, areaPrefix, number] = parts
    const isReginalNumber = internationalPrefix === '0'
    const isInternationalNumber = /\+[0-9]+/.test(internationalPrefix)
    if (!(isReginalNumber || isInternationalNumber)) {
      return phoneNumber
    }

    let prefix = internationalPrefix + areaPrefix
    if (isInternationalNumber) {
      prefix = [internationalPrefix, areaPrefix].join(' ')
    }

    return [prefix, ...number.split(/([0-9]{2})/g).filter((num) => num)].join(
      ' '
    )
  }
  return phoneNumber
}

export const Profile = () => {
  const { logEvent } = useAnalytics()

  const { currentUser: user } = useCurrentUser()
  return (
    <Card data-testid="card-profile">
      <div className={styles['header-row']}>
        <h3 className={styles['title']}>Profil</h3>

        <ButtonLink
          variant={ButtonVariant.TERNARY}
          link={{ to: '/profil', isExternal: false }}
          icon={fullEditIcon}
          onClick={() => logEvent(Events.CLICKED_EDIT_PROFILE)}
        >
          Modifier
        </ButtonLink>
      </div>

      <div>
        <ul className={styles['description-list']}>
          <li className={styles['description-item']}>
            <span className={styles['description-label']}>Nom :</span>
            <span className={styles['description-value']}>{user.lastName}</span>
          </li>
          <li className={styles['description-item']}>
            <span className={styles['description-label']}>Prénom :</span>
            <span className={styles['description-value']}>
              {user.firstName}
            </span>
          </li>
          <li className={styles['description-item']}>
            <span className={styles['description-label']}>Email :</span>
            <span className={styles['description-value']}>{user.email}</span>
          </li>
          <li className={styles['description-item']}>
            <span className={styles['description-label']}>Téléphone :</span>
            <span className={styles['description-value']}>
              {formatPhoneNumber(user.phoneNumber)}
            </span>
          </li>
          <li className={styles['description-item']}>
            <span className={styles['description-label']}>Mot de passe :</span>
            <span className={styles['description-value']}>***************</span>
          </li>
        </ul>
      </div>
    </Card>
  )
}
