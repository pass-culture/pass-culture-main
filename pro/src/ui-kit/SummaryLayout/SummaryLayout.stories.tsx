import { withRouter } from 'storybook-addon-remix-react-router'

import { SummaryContent } from './SummaryContent'
import { SummaryDescriptionList } from './SummaryDescriptionList'
import { SummaryLayout } from './SummaryLayout'
import { SummarySection } from './SummarySection'
import { SummarySubSection } from './SummarySubSection'

export default {
  title: '@/components/SummaryLayout',
  component: SummaryLayout,
  decorators: [withRouter],
}

const Template = () => (
  <div style={{ width: 780 }}>
    <SummaryLayout>
      <SummaryContent>
        <SummarySection title="Lorem ipsum dolor sit amet" editLink="/">
          <SummarySubSection title="Sub section title">
            <SummaryDescriptionList
              descriptions={[
                {
                  title: 'Lorem',
                  text: 'Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus.',
                },
              ]}
            />
          </SummarySubSection>
        </SummarySection>
        <SummarySection title="Lorem ipsum dolor sit amet" editLink="/">
          <SummarySubSection title="Sub section title">
            <SummaryDescriptionList
              descriptions={[
                {
                  title: 'Lorem',
                  text: 'Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus.',
                },
                {
                  title: 'Ipsum',
                  text: 'Lorem ipsum dolor sit amet',
                },
              ]}
            />
          </SummarySubSection>

          <SummarySubSection title="Sub section title">
            <SummaryDescriptionList descriptions={[{ text: 'Pas de titre' }]} />
          </SummarySubSection>

          <SummarySubSection title="Sub section title">
            <SummaryDescriptionList
              descriptions={[
                {
                  title: 'Lorem',
                  text: 'Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus.',
                },
                {
                  title: 'Ipsum',
                  text: 'Lorem ipsum dolor sit amet',
                },
              ]}
            />
          </SummarySubSection>
        </SummarySection>
      </SummaryContent>
    </SummaryLayout>
  </div>
)

export const Default = Template.bind({})
