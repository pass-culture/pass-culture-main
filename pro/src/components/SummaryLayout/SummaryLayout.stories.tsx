import React from 'react'
import { withRouter } from 'storybook-addon-react-router-v6'

import { SummaryContent } from './SummaryContent'
import { SummaryLayout } from './SummaryLayout'
import { SummaryRow } from './SummaryRow'
import { SummarySection } from './SummarySection'
import { SummarySubSection } from './SummarySubSection'

export default {
  title: 'components/SummaryLayout',
  component: SummaryLayout,
  decorators: [withRouter],
}

const Template = () => (
  <div style={{ width: 780 }}>
    <SummaryLayout>
      <SummaryContent>
        <SummarySection title="Lorem ipsum dolor sit amet" editLink="/">
          <SummarySubSection title="Sub section title">
            <SummaryRow
              description="Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus."
              title="Lorem"
            />
          </SummarySubSection>
        </SummarySection>
        <SummarySection title="Lorem ipsum dolor sit amet" editLink="/">
          <SummarySubSection title="Sub section title">
            <SummaryRow
              description="Description  : Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus."
              title="Lorem"
            />
            <SummaryRow
              description="Lorem ipsum dolor sit amet"
              title="Lorem"
            />
          </SummarySubSection>
          <SummarySubSection title="Sub section title">
            <SummaryRow description="Pas de titre" />
          </SummarySubSection>
          <SummarySubSection title="Sub section title">
            <SummaryRow
              description="Description  : Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus."
              title="Lorem"
            />
            <SummaryRow
              description="Lorem ipsum dolor sit amet"
              title="Lorem"
            />
          </SummarySubSection>
        </SummarySection>
      </SummaryContent>
    </SummaryLayout>
  </div>
)

export const Default = Template.bind({})
