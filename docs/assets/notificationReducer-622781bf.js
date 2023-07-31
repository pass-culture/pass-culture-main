import{r as y}from"./index-76fb7be0.js";import{r as q}from"./index-b0fbc9cc.js";import"./hoist-non-react-statics.cjs-3f8ebaa8.js";var M={exports:{}},P={};/**
 * @license React
 * use-sync-external-store-shim.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var l=y;function z(t,e){return t===e&&(t!==0||1/t===1/e)||t!==t&&e!==e}var W=typeof Object.is=="function"?Object.is:z,K=l.useState,Y=l.useEffect,U=l.useLayoutEffect,G=l.useDebugValue;function J(t,e){var o=e(),c=K({inst:{value:o,getSnapshot:e}}),r=c[0].inst,s=c[1];return U(function(){r.value=o,r.getSnapshot=e,N(r)&&s({inst:r})},[t,o,e]),Y(function(){return N(r)&&s({inst:r}),t(function(){N(r)&&s({inst:r})})},[t]),G(o),o}function N(t){var e=t.getSnapshot;t=t.value;try{var o=e();return!W(t,o)}catch{return!0}}function Q(t,e){return e()}var X=typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"?Q:J;P.useSyncExternalStore=l.useSyncExternalStore!==void 0?l.useSyncExternalStore:X;M.exports=P;var Z=M.exports,tt={};/**
 * @license React
 * use-sync-external-store-shim/with-selector.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var m=y,et=Z;function nt(t,e){return t===e&&(t!==0||1/t===1/e)||t!==t&&e!==e}var rt=typeof Object.is=="function"?Object.is:nt,ot=et.useSyncExternalStore,ut=m.useRef,ct=m.useEffect,st=m.useMemo,it=m.useDebugValue;tt.useSyncExternalStoreWithSelector=function(t,e,o,c,r){var s=ut(null);if(s.current===null){var f={hasValue:!1,value:null};s.current=f}else f=s.current;s=st(function(){function g(i){if(!k){if(k=!0,b=i,i=c(i),r!==void 0&&f.hasValue){var a=f.value;if(r(a,i))return d=a}return d=i}if(a=d,rt(b,i))return a;var F=c(i);return r!==void 0&&r(a,F)?a:(b=i,d=F)}var k=!1,b,d,B=o===void 0?null:o;return[function(){return g(e())},B===null?void 0:function(){return g(B())}]},[e,o,c,r]);var S=ot(t,s[0],s[1]);return ct(function(){f.hasValue=!0,f.value=S},[S]),it(S),S};function ft(t){t()}let V=ft;const at=t=>V=t,xt=()=>V,p=y.createContext(null);function lt(){return y.useContext(p)}var n={};/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var T=Symbol.for("react.element"),R=Symbol.for("react.portal"),v=Symbol.for("react.fragment"),$=Symbol.for("react.strict_mode"),h=Symbol.for("react.profiler"),x=Symbol.for("react.provider"),E=Symbol.for("react.context"),pt=Symbol.for("react.server_context"),O=Symbol.for("react.forward_ref"),C=Symbol.for("react.suspense"),_=Symbol.for("react.suspense_list"),I=Symbol.for("react.memo"),w=Symbol.for("react.lazy"),yt=Symbol.for("react.offscreen"),j;j=Symbol.for("react.module.reference");function u(t){if(typeof t=="object"&&t!==null){var e=t.$$typeof;switch(e){case T:switch(t=t.type,t){case v:case h:case $:case C:case _:return t;default:switch(t=t&&t.$$typeof,t){case pt:case E:case O:case w:case I:case x:return t;default:return e}}case R:return e}}}n.ContextConsumer=E;n.ContextProvider=x;n.Element=T;n.ForwardRef=O;n.Fragment=v;n.Lazy=w;n.Memo=I;n.Portal=R;n.Profiler=h;n.StrictMode=$;n.Suspense=C;n.SuspenseList=_;n.isAsyncMode=function(){return!1};n.isConcurrentMode=function(){return!1};n.isContextConsumer=function(t){return u(t)===E};n.isContextProvider=function(t){return u(t)===x};n.isElement=function(t){return typeof t=="object"&&t!==null&&t.$$typeof===T};n.isForwardRef=function(t){return u(t)===O};n.isFragment=function(t){return u(t)===v};n.isLazy=function(t){return u(t)===w};n.isMemo=function(t){return u(t)===I};n.isPortal=function(t){return u(t)===R};n.isProfiler=function(t){return u(t)===h};n.isStrictMode=function(t){return u(t)===$};n.isSuspense=function(t){return u(t)===C};n.isSuspenseList=function(t){return u(t)===_};n.isValidElementType=function(t){return typeof t=="string"||typeof t=="function"||t===v||t===h||t===$||t===C||t===_||t===yt||typeof t=="object"&&t!==null&&(t.$$typeof===w||t.$$typeof===I||t.$$typeof===x||t.$$typeof===E||t.$$typeof===O||t.$$typeof===j||t.getModuleId!==void 0)};n.typeOf=u;function A(t=p){const e=t===p?lt:()=>y.useContext(t);return function(){const{store:c}=e();return c}}const St=A();function dt(t=p){const e=t===p?St:A(t);return function(){return e().dispatch}}const Et=dt();at(q.unstable_batchedUpdates);const L="SET_IS_STICKYBAR_OPEN",D="CLOSE_NOTIFICATION",H="SHOW_NOTIFICATION",Ot=t=>({payload:t,type:H}),Ct=()=>({type:D}),_t=t=>({payload:t,type:L}),mt={isStickyBarOpen:!1,notification:null},It=(t=mt,e)=>{switch(e.type){case D:return{...t,notification:null};case H:return{...t,notification:e.payload};case L:return{...t,isStickyBarOpen:e.payload};default:return t}};export{p as R,_t as a,Ct as c,xt as g,It as n,Ot as s,Et as u};
//# sourceMappingURL=notificationReducer-622781bf.js.map
