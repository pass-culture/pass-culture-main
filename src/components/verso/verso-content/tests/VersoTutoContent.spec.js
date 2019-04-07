/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
// $(yarn bin)/jest --env=jsdom ./src/components/verso/verso-content/tests/VersoTutoContent.spec.js --watch
import React from 'react';
import { shallow } from 'enzyme';

import VersoTutoContent from '../VersoTutoContent';
import { THUMBS_URL } from '../../../../utils/config';

describe('src | components | verso | verso-content | VersoTutoContent', () => {
  it('should match snapshot', () => {
    // given
    const props = { mediationId: '1234' };
    // when
    const wrapper = shallow(<VersoTutoContent {...props} />);
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
    const wrapper = shallow(<VersoTutoContent {...props} />);
    const img = wrapper.find('img');
    // then
    expect(img).toHaveLength(1);
    expect(img.hasClass('verso-tuto-mediation')).toBe(true);
    expect(img.prop('src')).toEqual(url);
  });
});
