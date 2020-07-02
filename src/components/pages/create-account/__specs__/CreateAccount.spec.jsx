import { mount } from 'enzyme'
import React from 'react'
import { createMemoryHistory } from 'history'

import CreateAccount from '../CreateAccount'
import { MemoryRouter } from 'react-router'
import EligibilityCheck from '../EligibilityCheck/EligibilityCheck'
import Eligible from '../Eligible/Eligible'
import IneligibleDepartment from '../IneligibleDepartment/IneligibleDepartment'
import IneligibleOverEighteen from '../IneligibleOverEighteen/IneligibleOverEighteen'
import EligibleSoon from '../EligibleSoon/EligibleSoon'
import IneligibleUnderEighteen from '../IneligibleUnderEighteen/IneligibleUnderEighteen'
import ContactSaved from '../ContactSaved/ContactSaved'

describe('create account page', () => {
  let props

  beforeEach(() => {
    props = {
      location: { pathname: '/verification-eligibilite' },
      history: createMemoryHistory(),
    }
  })

  it('should render the right component for route /verification-eligibilite', () => {
    // when
    const wrapper = mount(
      <MemoryRouter initialEntries={[props.location.pathname]}>
        <CreateAccount {...props} />
      </MemoryRouter>
    )

    // then
    const eligibiliyCheckComponent = wrapper.find(EligibilityCheck)
    expect(eligibiliyCheckComponent).toHaveLength(1)
    expect(eligibiliyCheckComponent.prop('historyPush')).toBe(props.history.push)
    expect(eligibiliyCheckComponent.prop('pathname')).toBe(props.location.pathname)
  })

  it('should render the right component for route /verification-eligibilite/eligible', () => {
    // given
    props.location.pathname = '/verification-eligibilite/eligible'

    // when
    const wrapper = mount(
      <MemoryRouter initialEntries={[props.location.pathname]}>
        <CreateAccount {...props} />
      </MemoryRouter>
    )

    // then
    const eligibleComponent = wrapper.find(Eligible)
    expect(eligibleComponent).toHaveLength(1)
  })

  it('should render the right component for route /verification-eligibilite/departement-non-eligible', () => {
    // given
    props.location.pathname = '/verification-eligibilite/departement-non-eligible'

    // when
    const wrapper = mount(
      <MemoryRouter initialEntries={[props.location.pathname]}>
        <CreateAccount {...props} />
      </MemoryRouter>
    )

    // then
    const ineligibleDepartmentComponent = wrapper.find(IneligibleDepartment)
    expect(ineligibleDepartmentComponent).toHaveLength(1)
  })

  it('should render the right component for route /verification-eligibilite/bientot', () => {
    // given
    props.location.pathname = '/verification-eligibilite/bientot'

    // when
    const wrapper = mount(
      <MemoryRouter initialEntries={[props.location.pathname]}>
        <CreateAccount {...props} />
      </MemoryRouter>
    )

    // then
    const eligibleSoonComponent = wrapper.find(EligibleSoon)
    expect(eligibleSoonComponent).toHaveLength(1)
  })

  it('should render the right component for route /verification-eligibilite/pas-eligible', () => {
    // given
    props.location.pathname = '/verification-eligibilite/pas-eligible'

    // when
    const wrapper = mount(
      <MemoryRouter initialEntries={[props.location.pathname]}>
        <CreateAccount {...props} />
      </MemoryRouter>
    )

    // then
    const ineligibleOverEighteenComponent = wrapper.find(IneligibleOverEighteen)
    expect(ineligibleOverEighteenComponent).toHaveLength(1)
  })

  it('should render the right component for route /verification-eligibilite/trop-tot', () => {
    // given
    props.location.pathname = '/verification-eligibilite/trop-tot'

    // when
    const wrapper = mount(
      <MemoryRouter initialEntries={[props.location.pathname]}>
        <CreateAccount {...props} />
      </MemoryRouter>
    )

    // then
    const ineligibleUnderEighteenComponent = wrapper.find(IneligibleUnderEighteen)
    expect(ineligibleUnderEighteenComponent).toHaveLength(1)
  })

  it('should render the right component for route /verification-eligibilite/gardons-contact', () => {
    // given
    props.location.pathname = '/verification-eligibilite/gardons-contact'

    // when
    const wrapper = mount(
      <MemoryRouter initialEntries={[props.location.pathname]}>
        <CreateAccount {...props} />
      </MemoryRouter>
    )

    // then
    const contactSavedComponent = wrapper.find(ContactSaved)
    expect(contactSavedComponent).toHaveLength(1)
  })
})
