import { useState } from 'react'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { type FormatEnum, NatureEnum } from '@/apiClient/v1'
import { GET_NFD_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import strokeBookIcon from '@/icons/stroke-book.svg'
import strokeCardsIcon from '@/icons/stroke-cards.svg'
import strokeEventsIcon from '@/icons/stroke-events.svg'
import strokeNumIcon from '@/icons/stroke-num.svg'
import strokeRightIcon from '@/icons/stroke-right.svg'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './IndividualOfferV2NatureFormatDomain.module.scss'

const natureIcon: Record<NatureEnum, string> = {
  [NatureEnum.BIEN]: strokeBookIcon,
  [NatureEnum.CARTE_ABONNEMENT]: strokeCardsIcon,
  [NatureEnum.EVENEMENT]: strokeEventsIcon,
  [NatureEnum.NUMERIQUE]: strokeNumIcon,
}

const IndividualOfferV2NatureFormatDomain = (): JSX.Element => {
  const navigate = useNavigate()
  const [selectedNature, setSelectedNature] = useState<NatureEnum | null>(null)
  const [selectedFormat, setSelectedFormat] = useState<FormatEnum | null>(null)
  const nfdQuery = useSWR([GET_NFD_QUERY_KEY], () =>
    api.getNatureFormatDomain()
  )

  const onSubmit = async (event: React.SubmitEvent<HTMLFormElement>) => {
    event.preventDefault()
    await navigate('/offre/individuelle/v2/creation/description')
  }

  if (!nfdQuery.data) {
    return <Spinner />
  }

  const natures = nfdQuery.data
  return (
    <>
      <h2 className={styles['title']}>Nature et format</h2>
      <form onSubmit={onSubmit}>
        <div className={styles['nature']}>
          <RadioButtonGroup
            name="nature"
            label="Sélectionnez la nature"
            variant={'detailed'}
            checkedOption={selectedNature as string}
            display="horizontal"
            sizing="hug"
            onChange={(event) =>
              setSelectedNature(event.target.value as NatureEnum)
            }
            options={natures.map((nature) => ({
              label: nature.label,
              value: nature.name,
              asset: {
                variant: 'icon',
                src: natureIcon[nature.name],
              },
            }))}
          />
        </div>
        {selectedNature && (
          <div className={styles['format']}>
            <RadioButtonGroup
              name="format"
              label="Sélectionnez le format"
              variant={'detailed'}
              checkedOption={selectedFormat as string}
              display="horizontal"
              sizing="hug"
              onChange={(event) =>
                setSelectedFormat(event.target.value as FormatEnum)
              }
              options={
                natures
                  .find((nature) => nature.name === selectedNature)
                  ?.formats.map((format) => ({
                    sizing: 'hug',
                    label: format.label,
                    value: format.format,
                  })) ?? []
              }
            />
          </div>
        )}
        <ActionsBarSticky hasSideNav={false} isEmbedded={true}>
          <ActionsBarSticky.Left>
            <Button
              color={ButtonColor.NEUTRAL}
              variant={ButtonVariant.SECONDARY}
              onClick={async () => {
                await navigate('/')
              }}
              label="Annuler et quitter"
            />
          </ActionsBarSticky.Left>

          <ActionsBarSticky.Right>
            <Button
              type="submit"
              color={ButtonColor.BRAND}
              variant={ButtonVariant.PRIMARY}
              label="Étape suivante"
              icon={strokeRightIcon}
              iconPosition={IconPositionEnum.RIGHT}
            />
          </ActionsBarSticky.Right>
        </ActionsBarSticky>
      </form>
    </>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferV2NatureFormatDomain
