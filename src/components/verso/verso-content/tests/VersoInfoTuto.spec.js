/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
// $(yarn bin)/jest --env=jsdom ./src/components/verso/tests/VersoInfoTuto.spec.js --watch
import React from 'react';
import { shallow } from 'enzyme';

import VersoInfoTuto from '../VersoInfoTuto';
import { THUMBS_URL } from '../../../../utils/config';

describe('src | components | verso | VersoInfoTuto', () => {
  it('should match snapshot', () => {
    // given
    const props = { mediationId: '1234' };
    // when
    const wrapper = shallow(<VersoInfoTuto {...props} />);
    // then
    expect(wrapper).toBeDefined();
    expect(wrapper).toMatchSnapshot();
  });

  it('should have a classnamed element with sourced img', () => {
    // given
    const mediationId = '1234';
    const props = { mediationId };
    const url = `${THUMBS_URL}/mediations/${mediationId}_1`;
    // when
    const wrapper = shallow(<VersoInfoTuto {...props} />);
    const img = wrapper.find('img');
    // then
    expect(img).toHaveLength(1);
    expect(img.hasClass('verso-tuto-mediation')).toBe(true);
    expect(img.prop('src')).toEqual(url);
  });
});
