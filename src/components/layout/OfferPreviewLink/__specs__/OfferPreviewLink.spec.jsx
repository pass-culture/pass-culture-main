import { mount } from 'enzyme'
import React from 'react'

import OfferPreviewLink from '../OfferPreviewLink'

describe('src | OfferPreviewLink', () => {
  let props

  beforeEach(() => {
    props = {
      offerWebappUrl: 'http://webapp.url.app',
      onClick: jest.fn(),
    }
  })

  it('should display a link', () => {
    // when
    const wrapper = mount(<OfferPreviewLink {...props} />)

    // then
    const link = wrapper.find('a')
    expect(link.text()).toBe('Prévisualiser')
    expect(link.prop('href')).toBe(props.offerWebappUrl)
    expect(link.prop('onClick')).toBe(props.onClick)
    const tip = wrapper.find('span')
    expect(tip.prop('data-tip')).toBe('Ouvrir un nouvel onglet avec la prévisualisation de l’offre.')
    const icon = wrapper.find('Icon')
    expect(icon.prop('svg')).toBe('ico-eye')
  })
})
