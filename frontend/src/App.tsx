import React from 'react';

import GlobalStyle from './styles/global'
import MainChat from './page/MainChat';

const App: React.FC = () => {
  return (
    <>
      <MainChat/>
      <GlobalStyle/>
    </>

  );
}

export default App;