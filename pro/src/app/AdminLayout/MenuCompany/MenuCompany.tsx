import cn from 'classnames'
import React from 'react'
import { generatePath, matchPath, useLocation } from 'react-router'

import { useAppContext } from 'app/AppContext'
import { useNavigate } from 'hooks'
import { Title } from 'ui-kit'
import SelectInput from 'ui-kit/form/Select/SelectInput'

import stylesMenu from '../Menu/Menu.module.scss'

import { CompanyMenuItems } from './CompanyMenuItems'
import styles from './MenuCompany.module.scss'

interface IMenuCompanyProps {
  className?: string
}

const getCurrentCompanyRoutePath = (pathname: string) => {
  const pathList = [
    '/entreprises/:venueId/offres',
    '/entreprises/:venueId/reservations',
    // need to be last element to be the lastest found.
    '/entreprises/:venueId',
  ]

  return pathList.find(path => matchPath(pathname, path))
}

const MenuCompany = ({ className }: IMenuCompanyProps) => {
  const {
    shouldSelectOfferer,
    selectedOffererId,
    setSelectedOffererId,
    selectedVenueId,
    setSelectedVenueId,
    venues,
    offererNames,
  } = useAppContext()
  const location = useLocation()
  const navigate = useNavigate()

  const offererOptions = offererNames.map(item => {
    return {
      value: String(item.id),
      label: item.name,
    }
  })
  const venueOptions = venues.map(item => {
    return {
      value: String(item.id),
      label: item.name,
    }
  })

  const handleVenueOnChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedVenueId &&
      e.target.value !== selectedVenueId &&
      setSelectedVenueId(e.target.value)
    const nextPath = getCurrentCompanyRoutePath(location.pathname)
    if (nextPath !== undefined) {
      navigate(generatePath(nextPath, { venueId: e.target.value }))
    } else {
      navigate(`/entreprises/${e.target.value}`)
    }
  }
  const handleVenueOnClick = () => {
    const isCompanyPage =
      getCurrentCompanyRoutePath(location.pathname) !== undefined
    if (!isCompanyPage) {
      navigate(`/entreprises/${selectedVenueId}`)
    }
  }

  return (
    <nav className={cn(stylesMenu['menu'], className)}>
      <div className={styles['company-selector']}>
        {shouldSelectOfferer && (
          <div className={styles['offerer-selector']}>
            <Title level={5}>Structure juridique</Title>
            <SelectInput
              name="offerer"
              value={selectedOffererId || offererOptions[0].value}
              options={offererOptions}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
                setSelectedOffererId && setSelectedOffererId(e.target.value)
              }}
            />
          </div>
        )}
        {venues.length > 0 && (
          <div className={styles['venue-selector']}>
            <Title level={5}>Mon entreprise</Title>
            <SelectInput
              name="venue"
              value={selectedVenueId || venueOptions[0].value}
              options={venueOptions}
              onChange={handleVenueOnChange}
              onClick={handleVenueOnClick}
            />
          </div>
        )}
      </div>

      <CompanyMenuItems />
    </nav>
  )
}

export default MenuCompany
