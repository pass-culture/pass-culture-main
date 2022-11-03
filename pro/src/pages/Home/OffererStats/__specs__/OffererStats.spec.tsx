import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { MemoryRouter } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'

import OffererStats from '../OffererStats'

const mockLogEvent = jest.fn()

const renderOffererStats = () => {
  return render(
    <MemoryRouter initialEntries={['/accueil']}>
      <OffererStats />
    </MemoryRouter>
  )
}

describe('OffererStats', () => {
  describe('log events', () => {
    it('should log events when click on one box link', async () => {
      // When
      jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
        logEvent: mockLogEvent,
        setLogEvent: null,
      }))
      renderOffererStats()
      const viewStatsButton = screen.getAllByRole('link', {
        name: 'Voir le tableau',
      })[0]
      await userEvent.click(viewStatsButton)

      // Then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenCalledWith(
        Events.CLICKED_VIEW_OFFERER_STATS,
        { from: '/accueil' }
      )
    })
    it('should log events when click on view all stats', async () => {
      // When
      jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
        logEvent: mockLogEvent,
        setLogEvent: null,
      }))
      renderOffererStats()
      const viewAllStatsButton = screen.getByRole('link', {
        name: 'Voir toutes les statistiques',
      })
      await userEvent.click(viewAllStatsButton)

      // Then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenCalledWith(
        Events.CLICKED_VIEW_ALL_OFFERER_STATS,
        { from: '/accueil' }
      )
    })
  })
})
