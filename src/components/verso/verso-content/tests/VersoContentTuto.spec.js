<<<<<<< HEAD:src/components/verso/verso-content/tests/VersoContentTuto.spec.js
/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import React from 'react';
import { shallow } from 'enzyme';

import VersoContentTuto from '../VersoContentTuto';
import { THUMBS_URL } from '../../../../utils/config';
=======
import React from 'react'
import { shallow } from 'enzyme'

import VersoTutoContent from '../VersoTutoContent'
import { THUMBS_URL } from '../../../../utils/config'
>>>>>>> (PC-1546): updated logic when checking if offer is finished, updated tests to simplify reading, added missing tests:src/components/verso/verso-content/tests/VersoTutoContent.spec.js

describe('src | components | verso | verso-content | VersoContentTuto', () => {
  it('should match snapshot', () => {
    // given
    const props = { mediationId: '1234' }

    // when
<<<<<<< HEAD:src/components/verso/verso-content/tests/VersoContentTuto.spec.js
    const wrapper = shallow(<VersoContentTuto {...props} />);
=======
    const wrapper = shallow(<VersoTutoContent {...props} />)

>>>>>>> (PC-1546): updated logic when checking if offer is finished, updated tests to simplify reading, added missing tests:src/components/verso/verso-content/tests/VersoTutoContent.spec.js
    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('should have a classnamed element with sourced img', () => {
    // given
    const mediationId = '1234'
    const props = { mediationId }
    const url = `${THUMBS_URL}/mediations/${mediationId}_1`

    // when
<<<<<<< HEAD:src/components/verso/verso-content/tests/VersoContentTuto.spec.js
    const wrapper = shallow(<VersoContentTuto {...props} />);
    const img = wrapper.find('img');
=======
    const wrapper = shallow(<VersoTutoContent {...props} />)

>>>>>>> (PC-1546): updated logic when checking if offer is finished, updated tests to simplify reading, added missing tests:src/components/verso/verso-content/tests/VersoTutoContent.spec.js
    // then
    const img = wrapper.find('img')
    expect(img).toHaveLength(1)
    expect(img.hasClass('verso-tuto-mediation')).toBe(true)
    expect(img.prop('alt')).toBe('verso')
    expect(img.prop('src')).toEqual(url)
  })
})
