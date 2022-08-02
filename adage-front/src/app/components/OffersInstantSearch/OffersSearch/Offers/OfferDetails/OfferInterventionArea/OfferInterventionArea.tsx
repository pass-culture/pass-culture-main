import React from 'react'

import {
  departmentLabelByValue,
  ALL_FRANCE_OPTION_VALUE,
  MAINLAND_OPTION_VALUE,
  domtomOptions,
  departmentOptions,
} from 'app/constants/departmentOptions'

const getInterventionAreaLabels = (interventionArea: string[]): string => {
  const labels: string[] = []

  if (interventionArea.includes(ALL_FRANCE_OPTION_VALUE)) {
    return departmentLabelByValue[ALL_FRANCE_OPTION_VALUE]
  }

  if (interventionArea.includes(MAINLAND_OPTION_VALUE)) {
    labels.push(departmentLabelByValue[MAINLAND_OPTION_VALUE])

    domtomOptions.forEach(domtomOption => {
      if (interventionArea.includes(domtomOption.value.toString())) {
        const [departmentCode, departmentLabel] =
          domtomOption.label.split(' - ')
        labels.push(`${departmentLabel} (${departmentCode})`)
      }
    })

    return labels.join(' - ')
  }

  departmentOptions.forEach(interventionOption => {
    if (interventionArea.includes(interventionOption.value.toString())) {
      const [departmentCode, departmentLabel] =
        interventionOption.label.split(' - ')
      labels.push(`${departmentLabel} (${departmentCode})`)
    }
  })

  return labels.join(' - ')
}

const OfferInterventionArea = ({
  interventionArea,
}: {
  interventionArea: string[]
}): JSX.Element => <div>{getInterventionAreaLabels(interventionArea)}</div>

export default OfferInterventionArea
