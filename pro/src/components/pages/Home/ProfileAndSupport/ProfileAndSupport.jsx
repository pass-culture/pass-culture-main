import React, { useCallback, useState } from 'react'

import { Events } from 'core/FirebaseEvents/constants'
import Icon from 'components/layout/Icon'
import ProfileInformationsModal from './ProfileInformationsModal'
import { STEP_PROFILE_HASH } from '../HomepageBreadcrumb'
import Support from './Support'
import useCurrentUser from 'components/hooks/useCurrentUser'
import { useSelector } from 'react-redux'

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

    if (!parts.length === 3) return phoneNumber

    const [internationalPrefix, areaPrefix, number] = parts
    isReginalNumber = internationalPrefix === '0'
    isInternationalNumber = /\+[0-9]+/.test(internationalPrefix)
    if (!(isReginalNumber || isInternationalNumber)) return phoneNumber

    let prefix = internationalPrefix + areaPrefix
    if (isInternationalNumber) {
      prefix = [internationalPrefix, areaPrefix].join(' ')
    }

    return [prefix, ...number.split(/([0-9]{2})/g).filter(num => num)].join(' ')
  }
  return phoneNumber
}

const ProfileAndSupport = () => {
  const [isEditingProfile, setIsEditingProfile] = useState(false)
  const logEvent = useSelector(state => state.app.logEvent)

  const { currentUser: user } = useCurrentUser()

  const showProfileInfoModal = useCallback(() => {
    logEvent(Events.CLICKED_EDIT_PROFILE)
    setIsEditingProfile(true)
  }, [logEvent])

  const hideProfileInfoModal = useCallback(() => setIsEditingProfile(false), [])

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
              <button
                className="tertiary-button"
                onClick={showProfileInfoModal}
                type="button"
              >
                <Icon svg="ico-outer-pen" />
                Modifier
              </button>
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
              </ul>
            </div>
          </div>
        </div>
        <Support />
      </div>
      {isEditingProfile && (
        <ProfileInformationsModal
          hideProfileInfoModal={hideProfileInfoModal}
          user={user}
        />
      )}
    </>
  )
}

export default ProfileAndSupport
