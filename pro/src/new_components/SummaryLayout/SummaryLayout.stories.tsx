import React from 'react'
import { SummaryLayout } from '.'
import { withRouterDecorator } from 'stories/decorators/withRouter'

export default {
  title: 'components/SummaryLayout',
  component: SummaryLayout,
  decorators: [withRouterDecorator],
}

const Template = () => (
  <div style={{ width: 780 }}>
    <SummaryLayout>
      <SummaryLayout.Content>
        <SummaryLayout.Section title="Lorem ipsum dolor sit amet" editLink="/">
          <SummaryLayout.SubSection title="Sub section title">
            <SummaryLayout.Row
              description="Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus."
              title="Lorem"
            />
          </SummaryLayout.SubSection>
        </SummaryLayout.Section>
        <SummaryLayout.Section title="Lorem ipsum dolor sit amet" editLink="/">
          <SummaryLayout.SubSection title="Sub section title">
            <SummaryLayout.Row
              description="Description  : Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus."
              title="Lorem"
            />
            <SummaryLayout.Row
              description="Lorem ipsum dolor sit amet"
              title="Lorem"
            />
          </SummaryLayout.SubSection>
          <SummaryLayout.SubSection title="Sub section title">
            <SummaryLayout.Row description="Pas de titre" />
          </SummaryLayout.SubSection>
          <SummaryLayout.SubSection title="Sub section title">
            <SummaryLayout.Row
              description="Description  : Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus."
              title="Lorem"
            />
            <SummaryLayout.Row
              description="Lorem ipsum dolor sit amet"
              title="Lorem"
            />
          </SummaryLayout.SubSection>
        </SummaryLayout.Section>
      </SummaryLayout.Content>
    </SummaryLayout>
  </div>
)

export const Default = Template.bind({})
