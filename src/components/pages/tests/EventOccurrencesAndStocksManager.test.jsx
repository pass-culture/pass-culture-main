import React from 'react'
import { getAddUrl } from '../Offer/EventOccurrencesAndStocksManager'

describe('src | components | pages | EventOccurrencesAndStocksManager | getAddUrl', () => {
  it('should return an event add URL', () => {
    // given
    const isEditing = false
    const isStockOnly = false
    const offerId = 42
    const defaultUrl = `/offres/${offerId}`
    const stocks = []
    // when
    const url = getAddUrl(isEditing, isStockOnly, offerId, stocks, defaultUrl)
    // then
    expect(url).toBeDefined()
    expect(url).toEqual('/offres/42?gestion&date=nouvelle')
  })

  it('should return a thing add URL', () => {
    // given
    const isEditing = false
    const isStockOnly = true
    const offerId = 42
    const defaultUrl = `/offres/${offerId}`
    const stocks = []
    // when
    const url = getAddUrl(isEditing, isStockOnly, offerId, stocks, defaultUrl)
    // then
    expect(url).toBeDefined()
    expect(url).toEqual('/offres/42?gestion&stock=nouveau')
  })

  it('should return the default URL', () => {
    // given
    const isEditing = true
    const isStockOnly = false
    const offerId = 42
    const defaultUrl = `/offres/${offerId}`
    const stocks = []
    // when
    const url = getAddUrl(isEditing, isStockOnly, offerId, stocks, defaultUrl)
    // then
    expect(url).toBeDefined()
    expect(url).toEqual(defaultUrl)
  })

  it('should return the default URL', () => {
    // given
    const isEditing = true
    const isStockOnly = true
    const offerId = 42
    const defaultUrl = `/offres/${offerId}`
    const stocks = []
    // when
    const url = getAddUrl(isEditing, isStockOnly, offerId, stocks, defaultUrl)
    // then
    expect(url).toBeDefined()
    expect(url).toEqual(defaultUrl)
  })

  it('should return a thing edition URL (do not allow multuple thing stocks)', () => {
    // given
    const isEditing = false
    const isStockOnly = true
    const offerId = 42
    const defaultUrl = `/offres/${offerId}`
    const stocks = [{ id: 'FE' }]
    // when
    const url = getAddUrl(isEditing, isStockOnly, offerId, stocks, defaultUrl)
    // then
    expect(url).toBeDefined()
    expect(url).toEqual('/offres/42?gestion&stock=FE')
  })

  it('should return an event add URL (allow multiple event stocks)', () => {
    // given
    const isEditing = false
    const isStockOnly = false
    const offerId = 42
    const defaultUrl = `/offres/${offerId}`
    const stocks = [{ id: 'FE' }]
    // when
    const url = getAddUrl(isEditing, isStockOnly, offerId, stocks, defaultUrl)
    // then
    expect(url).toBeDefined()
    expect(url).toEqual('/offres/42?gestion&date=nouvelle')
  })
})
