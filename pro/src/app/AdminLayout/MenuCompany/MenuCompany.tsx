import cn from 'classnames'
import React from 'react'

import { useAppContext } from 'app/AppContext'
import { Title } from 'ui-kit'
import SelectInput from 'ui-kit/form/Select/SelectInput'

import stylesMenu from '../Menu/Menu.module.scss'

import { CompanyMenuItems } from './CompanyMenuItems'
import styles from './MenuCompany.module.scss'

interface IMenuCompanyProps {
  className?: string
}

const MenuCompany = ({ className }: IMenuCompanyProps) => {
  const {
    shouldSelectOfferer,
    selectedVenue,
    selectedOffererId,
    setSelectedOffererId,
    selectedVenueId,
    setSelectedVenueId,
    venues,
    offererNames,
  } = useAppContext()

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
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
                setSelectedVenueId && setSelectedVenueId(e.target.value)
              }}
            />
          </div>
        )}
      </div>

      <CompanyMenuItems />
    </nav>
  )
}

export default MenuCompany
