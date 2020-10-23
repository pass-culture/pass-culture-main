import { mount } from 'enzyme'
import React from 'react'
import Thumb from 'components/layout/Thumb'
import Icon from 'components/layout/Icon'
import LocalProviderInformation from '../LocalProviderInformation'

describe('src | LocalProviderInformationContainer', () => {
  let props

  beforeEach(() => {
    props = {
      offererId: 'ABCD',
      offerName: 'Super Livre',
      providerInfo: {
        icon: 'localProviderStocks',
        name: 'localProvider',
      },
      thumbUrl: 'http://localhost/storage/thumbs/products/AERTR',
      venueId: 'EARZ',
    }
  })

  it('should display an offer image', () => {
    // when
    const wrapper = mount(<LocalProviderInformation {...props} />)

    // then
    const thumb = wrapper.find(Thumb)
    expect(thumb.prop('url')).toBe('http://localhost/storage/thumbs/products/AERTR')
  })

  it('should display a link to venue page', () => {
    // when
    const wrapper = mount(<LocalProviderInformation {...props} />)

    // then
    const tooltip = wrapper.find('span')
    expect(tooltip.prop('data-tip')).toContain('<a href="/structures/ABCD/lieux/EARZ">')
  })

  it('should display provider information', () => {
    // Given
    const wrapper = mount(<LocalProviderInformation {...props} />)

    // When
    const title = wrapper.find({ children: 'Offre synchronisée avec localProvider' })
    const paragraphe = wrapper.find({
      children:
        'Le visuel par défaut, les informations et le stock de cette offre sont synchronisés avec les données localProvider tous les soirs.',
    })
    const logo = wrapper.find(Icon)

    // Then
    expect(title).toHaveLength(1)
    expect(logo.at(0).prop('svg')).toBe('localProviderStocks')
    expect(paragraphe).toHaveLength(1)
  })
})
