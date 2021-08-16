import React, { useCallback, useEffect, useState } from 'react'

import AppLayout from 'app/AppLayout'
import Banner from 'components/layout/Banner/Banner'
import CsvTableButtonContainer from 'components/layout/CsvTableButton/CsvTableButtonContainer'
import DownloadButtonContainer from 'components/layout/DownloadButton/DownloadButtonContainer'
import Icon from 'components/layout/Icon'
import PeriodSelector from 'components/layout/inputs/PeriodSelector/PeriodSelector'
import Select from 'components/layout/inputs/Select'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import * as pcapi from 'repository/pcapi/pcapi'
import { API_URL } from 'utils/config'
import { getToday, formatBrowserTimezonedDateAsUTC, FORMAT_ISO_DATE_ONLY } from 'utils/date'

import './Reimbursement.scss'

const dateFilterFormat = date => formatBrowserTimezonedDateAsUTC(date, FORMAT_ISO_DATE_ONLY)

const today = getToday()

const oneMonthAGo = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate())

const ALL_VENUES_OPTION_ID = 'allVenues'

const INITIAL_FILTERS = {
  venue: ALL_VENUES_OPTION_ID,
  periodStart: oneMonthAGo,
  periodEnd: today,
}

const INITIAL_CSV_URL = `${API_URL}/reimbursements/csv`

const buildCsvUrlWithParameters = filters => {
  let url = new URL(INITIAL_CSV_URL)

  if (filters.venue && filters.venue !== ALL_VENUES_OPTION_ID) {
    url.searchParams.set('venueId', filters.venue)
  }

  if (filters.periodStart) {
    url.searchParams.set('reimbursementPeriodBeginningDate', dateFilterFormat(filters.periodStart))
  }

  if (filters.periodEnd) {
    url.searchParams.set('reimbursementPeriodEndingDate', dateFilterFormat(filters.periodEnd))
  }

  return url.toString()
}

const sortByKeyAlphabeticalOrder = keyName => (x, y) => x[keyName].localeCompare(y[keyName])

const buildAndSortVenueFilterOptions = venues =>
  venues
    .map(venue => ({
      id: venue.id,
      displayName: venue.isVirtual
        ? `${venue.offererName} - Offre numérique`
        : venue.publicName || venue.name,
    }))
    .sort(sortByKeyAlphabeticalOrder('displayName'))

const Reimbursements = () => {
  const [venuesOptions, setVenuesOptions] = useState([])
  const [filters, setFilters] = useState(INITIAL_FILTERS)
  const [csvUrl, setCsvUrl] = useState(INITIAL_CSV_URL)

  const loadVenues = useCallback(async () => {
    try {
      const venuesResponse = await pcapi.getVenuesForOfferer({ activeOfferersOnly: true })
      const selectOptions = buildAndSortVenueFilterOptions(venuesResponse)
      setVenuesOptions(selectOptions)
    } catch (err) {
      console.error(err)
    }
  }, [setVenuesOptions])

  const setVenueFilter = useCallback(
    event => {
      const venueId = event.target.value
      setFilters(prevFilters => ({ ...prevFilters, venue: venueId }))
    },
    [setFilters]
  )

  const setStartDateFilter = useCallback(
    startDate => {
      setFilters(prevFilters => ({ ...prevFilters, periodStart: startDate }))
    },
    [setFilters]
  )

  const setEndDateFilter = useCallback(
    endDate => {
      setFilters(prevFilters => ({ ...prevFilters, periodEnd: endDate }))
    },
    [setFilters]
  )

  function resetFilters() {
    setFilters(INITIAL_FILTERS)
  }

  useEffect(() => {
    loadVenues()
  }, [loadVenues])

  useEffect(() => {
    setCsvUrl(buildCsvUrlWithParameters(filters))
  }, [filters])

  return (
    <AppLayout
      layoutConfig={{
        pageName: 'reimbursements',
      }}
    >
      <PageTitle title="Vos remboursements" />
      <Titles title="Remboursements" />
      {venuesOptions.length ? (
        <>
          <p>
            Les remboursements s’effectuent tous les 15 jours, rétroactivement suite à la validation d’une contremarque dans le guichet ou à la validation automatique des contremarques d’évènements. Cette page est automatiquement mise à jour à chaque remboursement.
          </p>
          <Banner type="notification-info">
            En savoir plus sur
            <a
              className="bi-link tertiary-link"
              href="https://aide.passculture.app/fr/articles/5096833-acteurs-culturels-quel-est-le-calendrier-des-prochains-remboursements"
              rel="noopener noreferrer"
              target="_blank"
            >
              <Icon svg="ico-external-site" />
              Les prochains remboursements
            </a>
            <a
              className="bi-link tertiary-link"
              href="https://aide.passculture.app/fr/articles/5096171-acteurs-culturels-comment-determiner-ses-modalites-de-remboursement"
              rel="noopener noreferrer"
              target="_blank"
            >
              <Icon svg="ico-external-site" />
              Les modalités de remboursement
            </a>
          </Banner>

          <div className="header">
            <h2 className="header-title">
              Affichage des remboursements
            </h2>
            <button
              className="tertiary-button"
              onClick={resetFilters}
              type="button"
            >
              Réinitialiser les filtres
            </button>
          </div>

          <div className="filters">
            <Select
              defaultOption={{ displayName: 'Tous les lieux', id: ALL_VENUES_OPTION_ID }}
              handleSelection={setVenueFilter}
              label="Lieu"
              name="lieu"
              options={venuesOptions}
              selectedValue={filters.venue}
              size="20"
            />
            <PeriodSelector
              changePeriodBeginningDateValue={setStartDateFilter}
              changePeriodEndingDateValue={setEndDateFilter}
              isDisabled={false}
              label="Période"
              maxDateEnding={getToday()}
              periodBeginningDate={filters.periodStart}
              periodEndingDate={filters.periodEnd}
              todayDate={getToday()}
            />
          </div>

          <div className="button-group">
            <span className="button-group-separator" />
            <div className="button-group-buttons">
              <DownloadButtonContainer
                filename="remboursements_pass_culture"
                href={csvUrl}
                isDisabled={!filters.periodStart || !filters.periodEnd}
                mimeType="text/csv"
              >
                Télécharger
              </DownloadButtonContainer>
              <CsvTableButtonContainer
                href={csvUrl}
                isDisabled={!filters.periodStart || !filters.periodEnd}
              >
                Afficher
              </CsvTableButtonContainer>
            </div>
          </div>

          <p className="format-mention">
            Le fichier est au format CSV, compatible avec tous les tableurs et éditeurs de texte.
          </p>
        </>
      ) : (
        <Spinner />
      )}
    </AppLayout>
  )
}

export default Reimbursements
