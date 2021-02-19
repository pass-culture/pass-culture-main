import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'

import { steps, STEP_ID_PROFILE } from '../HomepageBreadcrumb'

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

    let internationalPrefix, areaPrefix, number, isReginalNumber, isInternationalNumber
    let isValid = parts.length === 3
    if (isValid) {
      [internationalPrefix, areaPrefix, number] = parts
      isReginalNumber = internationalPrefix === '0'
      isInternationalNumber = /\+[0-9]+/.test(internationalPrefix)
      isValid = isReginalNumber || isInternationalNumber
    }

    if (!isValid) {
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

const Profile = ({ user }) => {
  return (
    <>
      <h2
        className="h-section-title"
        id={steps[STEP_ID_PROFILE].hash}
      >
        {'Profil et aide'}
      </h2>

      <div className="h-section-row">
        <div className="h-card h-card-secondary-hover">
          <div className="h-card-inner">
            <div className="h-card-header-row">
              <h3 className="h-card-title">
                {'Profil'}
              </h3>
              <Link
                className="tertiary-link"
                to="/profil"
              >
                <Icon svg="ico-outer-pen" />
                {'Modifier'}
              </Link>
            </div>
            <div className="h-card-content">
              <ul className="h-description-list">
                <li className="h-dl-row">
                  <span className="h-dl-title">
                    {'Nom :'}
                  </span>
                  <span className="h-dl-description">
                    {user.lastName}
                  </span>
                </li>
                <li className="h-dl-row">
                  <span className="h-dl-title">
                    {'Prénom :'}
                  </span>
                  <span className="h-dl-description">
                    {user.firstName}
                  </span>
                </li>
                <li className="h-dl-row single-line">
                  <span className="h-dl-title">
                    {'E-mail :'}
                  </span>
                  <span className="h-dl-description">
                    {user.email}
                  </span>
                </li>
                <li className="h-dl-row">
                  <span className="h-dl-title">
                    {'Téléphone :'}
                  </span>
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
    </>
  )
}

Profile.propTypes = {
  user: PropTypes.shape().isRequired,
}

export default Profile
