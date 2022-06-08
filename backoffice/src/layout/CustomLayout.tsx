import * as React from 'react';
import { Layout, LayoutProps } from 'react-admin';
import CustomAppBar from './CustomAppBar';
import Menu from './CustomMenu';

export default (props: LayoutProps) => {
    return <Layout {...props} appBar={CustomAppBar} sidebar={Menu} />;
};
