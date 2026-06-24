import './App.css';
import SearchComponent from './components/SearchComponent';
import Navbar from './components/page/Navbar';
import Footer from './components/page/Footer';
import Home from './components/page/Home';
import Work from './components/WorkComponent';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import CompetencyQuestionComponent from './components/CompetencyQuestionComponent';
import ExplorerComponent from './components/ExploreComponent';
import About from './components/page/About';
import { useState, useEffect } from 'react';

function App() {
  const [showScrollTop, setShowScrollTop] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      const boxContent = document.querySelector('[class*="box-content"]')
      if (boxContent) {
        setShowScrollTop(boxContent.scrollTop > 300)
      }
    }

    const boxContent = document.querySelector('[class*="box-content"]')
    if (boxContent) {
      boxContent.addEventListener('scroll', handleScroll)
    }

    return () => {
      const boxContent = document.querySelector('[class*="box-content"]')
      if (boxContent) {
        boxContent.removeEventListener('scroll', handleScroll)
      }
    }
  }, [])

  const scrollToTop = () => {
    const boxContent = document.querySelector('[class*="box-content"]')
    if (boxContent) {
      boxContent.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path='/' element={<Home />} />
        <Route index element={<Home />} />
        <Route path='ExploreAWork' element={<ExplorerComponent />} />
        <Route path='ExploreTheCorpus' element={<SearchComponent />} />
        <Route path='CompetencyQuestion' element={<CompetencyQuestionComponent />} />
        <Route path='Work' element={<Work />} />
        <Route path='About' element={<About />} />
      </Routes>
      <Footer />
      {showScrollTop && (
        <button onClick={scrollToTop} style={{
          position: 'fixed',
          bottom: '80px',
          right: '24px',
          background: '#9A6530',
          color: 'white',
          border: 'none',
          borderRadius: '50%',
          width: '44px',
          height: '44px',
          fontSize: '1.2rem',
          cursor: 'pointer',
          boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
          zIndex: 999
        }}>↑</button>
      )}
    </BrowserRouter>
  );
}

export default App;