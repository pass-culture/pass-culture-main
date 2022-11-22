import React from 'react'

import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import { ReactComponent as EditIcon } from 'icons/ico-pen-black.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { STEP_PROFILE_HASH } from '../HomepageBreadcrumb'

import Support from './Support'

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
export const formatPhoneNumber = phoneNumber => {
  let formatedNumber = phoneNumber
  if (phoneNumber) {
    formatedNumber = phoneNumber.replace(/ /g, '')
    const r = /(\+?[0-9]+)([0-9])([0-9]{8})/g
    const parts = formatedNumber.split(r).slice(1, -1)

    let isReginalNumber, isInternationalNumber

    if (!parts.length === 3) {
      return phoneNumber
    }

    const [internationalPrefix, areaPrefix, number] = parts
    isReginalNumber = internationalPrefix === '0'
    isInternationalNumber = /\+[0-9]+/.test(internationalPrefix)
    if (!(isReginalNumber || isInternationalNumber)) {
      return phoneNumber
    }

    let prefix = internationalPrefix + areaPrefix
    if (isInternationalNumber) {
      prefix = [internationalPrefix, areaPrefix].join(' ')
    }

    return [prefix, ...number.split(/([0-9]{2})/g).filter(num => num)].join(' ')
  }
  return phoneNumber
}

const ProfileAndSupport = () => {
  const { logEvent } = useAnalytics()

  const { currentUser: user } = useCurrentUser()
  return (
    <>
      <h2 className="h-section-title" id={STEP_PROFILE_HASH}>
        Profil et aide
      </h2>

      <div className="h-section-row">
        <div
          className="h-card h-card-secondary-hover"
          data-testid="card-profile"
        >
          <div className="h-card-inner">
            <div className="h-card-header-row">
              <h3 className="h-card-title">Profil</h3>
              <ButtonLink
                variant={ButtonVariant.TERNARY}
                link={{ to: '/profil', isExternal: false }}
                type="button"
                Icon={EditIcon}
                onClick={() => logEvent?.(Events.CLICKED_EDIT_PROFILE)}
              >
                Modifier
              </ButtonLink>
            </div>
            <div className="h-card-content">
              <ul className="h-description-list">
                <li className="h-dl-row">
                  <span className="h-dl-title">Nom :</span>
                  <span className="h-dl-description">{user.lastName}</span>
                </li>
                <li className="h-dl-row">
                  <span className="h-dl-title">Prénom :</span>
                  <span className="h-dl-description">{user.firstName}</span>
                </li>
                <li className="h-dl-row">
                  <span className="h-dl-title">E-mail :</span>
                  <span className="h-dl-description">{user.email}</span>
                </li>
                <li className="h-dl-row">
                  <span className="h-dl-title">Téléphone :</span>
                  <span className="h-dl-description">
                    {formatPhoneNumber(user.phoneNumber)}
                  </span>
                </li>
                <li className="h-dl-row">
                  <span className="h-dl-title">Mot de passe :</span>
                  <span className="h-dl-description">***************</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <Support />
      </div>
    </>
  )
}

export default ProfileAndSupport
