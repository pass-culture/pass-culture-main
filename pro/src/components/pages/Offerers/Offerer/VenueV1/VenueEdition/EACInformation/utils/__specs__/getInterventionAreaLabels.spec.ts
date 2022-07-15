import {
  ALL_FRANCE_OPTION_LABEL,
  ALL_FRANCE_OPTION_VALUE,
  CULTURAL_PARTNER_OPTION_LABEL,
  CULTURAL_PARTNER_OPTION_VALUE,
  MAINLAND_OPTION_LABEL,
  MAINLAND_OPTION_VALUE,
  allDepartmentValues,
  domtomOptions,
  mainlandOptions,
  mainlandValues,
} from 'core/Venue'

import { getInterventionAreaLabels } from '../getInterventionAreaLabels'

describe('getInterventionAreaLabels', () => {
  it('when it is all france', () => {
    expect(
      getInterventionAreaLabels([
        ALL_FRANCE_OPTION_VALUE,
        ...allDepartmentValues,
      ])
    ).toStrictEqual(ALL_FRANCE_OPTION_LABEL)
  })

  it('when it is only mainland', () => {
    expect(
      getInterventionAreaLabels([MAINLAND_OPTION_VALUE, ...mainlandValues])
    ).toStrictEqual(MAINLAND_OPTION_LABEL)
  })

  it('when it is mainland + some domtom', () => {
    expect(
      getInterventionAreaLabels([
        MAINLAND_OPTION_VALUE,
        ...mainlandValues,
        domtomOptions[0].value.toString(),
      ])
    ).toStrictEqual(`${MAINLAND_OPTION_LABEL}, ${domtomOptions[0].label}`)
  })

  it('when it is mainland + some domtom + offerer', () => {
    expect(
      getInterventionAreaLabels([
        MAINLAND_OPTION_VALUE,
        ...mainlandValues,
        domtomOptions[0].value.toString(),
        CULTURAL_PARTNER_OPTION_VALUE,
      ])
    ).toStrictEqual(
      `${CULTURAL_PARTNER_OPTION_LABEL}, ${MAINLAND_OPTION_LABEL}, ${domtomOptions[0].label}`
    )
  })

  it('when it is some departments', () => {
    expect(
      getInterventionAreaLabels([
        mainlandOptions[0].value.toString(),
        domtomOptions[0].value.toString(),
      ])
    ).toStrictEqual(`${mainlandOptions[0].label}, ${domtomOptions[0].label}`)
  })
})
