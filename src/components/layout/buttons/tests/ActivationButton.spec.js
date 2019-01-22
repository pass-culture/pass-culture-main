/* eslint
  react/jsx-one-expression-per-line: 0 */
// jest --env=jsdom ./src/components/layout/buttons/tests/ActivationButton --watch
import React from 'react'
import { shallow } from 'enzyme'
import ActivationButton from '../ActivationButton'

describe('src | components | layout | buttons | ActivationButton', () => {
  describe('snapshot', () => {
    it('whithout props', () => {
      // when
      const wrapper = shallow(<ActivationButton />)
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
    it('whith props', () => {
      // given
      const props = {
        className: 'pc-theme-gradient px18 pb18 pt16 fs20',
        onClickHandler: jest.fn(),
        style: { borderRadius: 4 },
      }
      // when
      const wrapper = shallow(
        <ActivationButton {...props}>
          <span>Activez votre pass Culture</span>
        </ActivationButton>
      )
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
