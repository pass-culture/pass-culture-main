// $(yarn bin)/jest --env=jsdom ./src/components/verso/verso-controls/favorite/tests/VersoButtonFavorite.spec.js --watch
import React from 'react'
import { shallow } from 'enzyme'
import { Icon } from 'pass-culture-shared'

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
  it('should use deactivated icon if is favorite', () => {
    // given
    const props = {
      isFavorite: true,
      onClick: jest.fn(),
    }
    // when
    const wrapper = shallow(<VersoButtonFavorite {...props} />)
    const iconProps = wrapper.find(Icon).props()
    // then
    expect(iconProps.alt).toEqual('Retirer des favoris')
    expect(iconProps.svg).toEqual('ico-like-w-on')
  })
  it('should use deactivated icon', () => {
    // given
    const props = {
      isFavorite: false,
      onClick: jest.fn(),
    }
    // when
    const wrapper = shallow(<VersoButtonFavorite {...props} />)
    const iconProps = wrapper.find(Icon).props()
    // then
    expect(iconProps.alt).toEqual('Ajouter aux favoris')
    expect(iconProps.svg).toEqual('ico-like-w')
  })
})
