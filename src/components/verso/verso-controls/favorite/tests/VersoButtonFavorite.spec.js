// $(yarn bin)/jest --env=jsdom ./src/components/verso/verso-controls/favorite/tests/VersoButtonFavorite.spec.js --watch
import React from 'react'
import { shallow } from 'enzyme'

import VersoButtonFavorite from '../VersoButtonFavorite'

describe('src | components | VersoButtonFavorite', () => {
  it('should match snapshot, with required props', () => {
    // given
    const props = { onClick: jest.fn() }

    // when
    const wrapper = shallow(<VersoButtonFavorite {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('should display remove to favorite icon', () => {
    // given
    const props = {
      isFavorite: true,
      onClick: jest.fn(),
    }

    // when
    const wrapper = shallow(<VersoButtonFavorite {...props} />)
    const iconProps = wrapper.find('span').props()

    // then
    expect(iconProps.title).toStrictEqual('Retirer des favoris')
    expect(iconProps.className).toStrictEqual('icon-ico-like-on')
  })

  it('should display add to favorite icon', () => {
    // given
    const props = {
      isFavorite: false,
      onClick: jest.fn(),
    }

    // when
    const wrapper = shallow(<VersoButtonFavorite {...props} />)
    const iconProps = wrapper.find('span').props()

    // then
    expect(iconProps.title).toStrictEqual('Ajouter aux favoris')
    expect(iconProps.className).toStrictEqual('icon-ico-like')
  })
})
