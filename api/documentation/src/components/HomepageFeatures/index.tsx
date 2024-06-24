import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  description: JSX.Element;
  imageUrl: string;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Manage a stock of goods',
    imageUrl: '/img/manage_stock.jpg',
    description: (
      <>
        With pass Culture API you will be able to create and manage easy all your stocks, whether you are a bookshop, a music shop or a digital platform. 
      </>
    ),
  },
  {
    title: 'Manage events for individual beneficiaries',
    imageUrl: '/img/theater.jpg',
    description: (
      <>
        If you are a concert hall, a theater, a museum, a movie theater, or other cultural partner organizing events, pass Culture API will help you manage your gauge and directly send tickets to beneficiary. 
      </>
    ),
  },
  {
    title: 'Manage events for scholar groups',
    imageUrl: '/img/scholar_group.jpg',
    description: (
      <>
        The pass Culture API enables you to create bookable offers for scholar groups. 
      </>
    ),
  },
  {
    title: 'Request your integration access',
    imageUrl: '/img/integration_access.jpg',
    description: (
      <>
        <a href='https://passculture.typeform.com/to/JHmbK9Hg'>Fill this form</a> to obtain your access. You will receive your dedicated API key and an access to your integration environment so you can see the situation for pass Culture users : beneficiary user and cultural actor user.. 
      </>
    ),
  },
  {
    title: 'Develop your integration',
    imageUrl: '/img/your_integration.jpg',
    description: (
      <>
        In this documentation, you will find tutorials to help you design your integration and all the different resources. Do not hesitate to download our openAPI specifications and reuse it in Postman for instance.
      </>
    ),
  },
  {
    title: 'Obtain your production access',
    imageUrl: '/img/production_access.jpg',
    description: (
      <>
        Once your integration is completed, we will ask you a short documentation of it that we will published on our help center and a quick demo. If your integration is public, we can organize a share communication.
      </>
    ),
  },
];

function Feature({title, description, imageUrl}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <img src={imageUrl} className={styles.featureSvg} />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): JSX.Element {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
